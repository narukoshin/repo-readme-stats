from base64 import b64encode
from os import environ, makedirs
from os.path import dirname, join
from random import choice
from re import sub
from shutil import copy, rmtree
from string import ascii_letters

from git.exc import GitCommandError
from git import Repo, Actor
from github import Auth, Github

from manager_environment import EnvironmentManager as EM
from manager_file import FileManager as FM
from manager_debug import DebugManager as DBM


def init_github_manager():
    GitHubManager.prepare_github_env()
    DBM.i(f"Target repo: {EM.REPO_OWNER}/{EM.REPO_NAME}.")


class GitHubManager:
    REPO: Repo
    REMOTE: object

    _REMOTE_NAME: str
    _REMOTE_PATH: str
    _SINGLE_COMMIT_BRANCH = "latest_branch"

    _START_COMMENT = f"<!--START_SECTION:{EM.SECTION_NAME}-->"
    _END_COMMENT = f"<!--END_SECTION:{EM.SECTION_NAME}-->"
    _README_REGEX = f"{_START_COMMENT}[\\s\\S]+{_END_COMMENT}"

    _AUTH_USER = None

    @staticmethod
    def prepare_github_env():
        github = Github(auth=Auth.Token(EM.GH_TOKEN))
        try:
            GitHubManager._AUTH_USER = github.get_user()
            DBM.i(f"Authenticated as: {GitHubManager._AUTH_USER.login}")
            if GitHubManager._AUTH_USER.email:
                DBM.i(f"User email: {GitHubManager._AUTH_USER.email}")
            else:
                DBM.i("User has no public email, will use noreply fallback")
        except Exception as e:
            DBM.w(f"Could not fetch authenticated user: {e}")
            GitHubManager._AUTH_USER = None
        clone_path = "repo"

        GitHubManager._REMOTE_NAME = f"{EM.REPO_OWNER}/{EM.REPO_NAME}"
        GitHubManager._REPO_PATH = f"https://{EM.GH_TOKEN}@github.com/{GitHubManager._REMOTE_NAME}.git"

        if EM.DEBUG_RUN:
            GitHubManager.REMOTE = None
            GitHubManager.REPO = None
            return

        GitHubManager.REMOTE = github.get_repo(GitHubManager._REMOTE_NAME)

        rmtree(clone_path, ignore_errors=True)
        GitHubManager.REPO = Repo.clone_from(GitHubManager._REPO_PATH, to_path=clone_path)

        if EM.COMMIT_SINGLE:
            GitHubManager.REPO.git.checkout(GitHubManager.branch(EM.PULL_BRANCH_NAME))
            GitHubManager.REPO.git.checkout("--orphan", GitHubManager._SINGLE_COMMIT_BRANCH)
        else:
            GitHubManager.REPO.git.checkout(GitHubManager.branch(EM.PUSH_BRANCH_NAME))

    @staticmethod
    def _get_author() -> Actor:
        user = GitHubManager._AUTH_USER
        if EM.COMMIT_BY_ME and user:
            fallback_email = f"{user.id}+{user.login}@users.noreply.github.com"
            author = Actor(
                EM.COMMIT_USERNAME or user.login,
                EM.COMMIT_EMAIL or user.email or fallback_email,
            )
            DBM.i(f"Commit author: {author.name} <{author.email}>")
            return author
        else:
            DBM.i(f"Using default identity (COMMIT_BY_ME={EM.COMMIT_BY_ME}, user={'set' if user else 'None'})")
            author = Actor(
                EM.COMMIT_USERNAME or "readme-bot",
                EM.COMMIT_EMAIL or "41898282+github-actions[bot]@users.noreply.github.com",
            )
            DBM.i(f"Commit author: {author.name} <{author.email}>")
            return author

    @staticmethod
    def branch(requested_branch: str) -> str:
        return GitHubManager.REMOTE.default_branch if requested_branch == "" else requested_branch

    @staticmethod
    def _copy_file_and_add_to_repo(src_path: str):
        dst_path = join(GitHubManager.REPO.working_tree_dir, src_path)
        makedirs(dirname(dst_path), exist_ok=True)
        copy(src_path, dst_path)
        try:
            GitHubManager.REPO.git.add(dst_path, force=EM.FORCE_ADD)
        except GitCommandError as e:
            if "ignored" in str(e):
                DBM.p(f"Potential Config Error!: '{src_path}' is ignored by .gitignore and was not added.")
                DBM.p("To fix this, set the 'FORCE_ADD' flag in your workflow file to 'True'.")
            raise

    @staticmethod
    def update_readme(stats: str):
        DBM.i("Updating README...")
        readme_path = join(GitHubManager.REPO.working_tree_dir, GitHubManager.REMOTE.get_readme().path)
        with open(readme_path, "r") as readme_file:
            readme_contents = readme_file.read()
        readme_stats = f"{GitHubManager._START_COMMENT}\n{stats}\n{GitHubManager._END_COMMENT}"
        new_readme = sub(GitHubManager._README_REGEX, readme_stats, readme_contents)
        with open(readme_path, "w") as readme_file:
            readme_file.write(new_readme)
        GitHubManager.REPO.git.add(readme_path)
        DBM.g("README updated!")

    @staticmethod
    def update_chart(name: str, path: str) -> str:
        output = str()
        DBM.i(f"Updating {name} chart...")
        if not EM.DEBUG_RUN:
            DBM.i("\tAdding chart to repo...")
            GitHubManager._copy_file_and_add_to_repo(path)
            chart_path = f"https://raw.githubusercontent.com/{GitHubManager._REMOTE_NAME}/{GitHubManager.branch(EM.PUSH_BRANCH_NAME)}/{path}"
            output += f"![{name} chart]({chart_path})\n\n"
        else:
            DBM.i("\tInlining chart...")
            hint = "You can use [this website](https://codebeautify.org/base64-to-image-converter) to view the generated base64 image."
            with open(path, "rb") as input_file:
                output += f"{hint}\n```\ndata:image/png;base64,{b64encode(input_file.read()).decode('utf-8')}\n```\n\n"
        return output

    @staticmethod
    def commit_update():
        actor = GitHubManager._get_author()
        DBM.i("Committing files to repo...")
        GitHubManager.REPO.index.commit(EM.COMMIT_MESSAGE, author=actor, committer=actor)
        if EM.COMMIT_SINGLE:
            DBM.i("Pushing files to repo as a single commit...")
            refspec = f"{GitHubManager._SINGLE_COMMIT_BRANCH}:{GitHubManager.branch(EM.PUSH_BRANCH_NAME)}"
            headers = GitHubManager.REPO.remotes.origin.push(force=True, refspec=refspec)
        else:
            DBM.i("Pushing files to repo...")
            headers = GitHubManager.REPO.remotes.origin.push()
        if len(headers) == 0:
            DBM.i(f"Repository push error: {headers}!")
        else:
            DBM.i("Repository synchronized!")

    @staticmethod
    def set_github_output(stats: str):
        DBM.i("Setting README contents as action output...")
        if "GITHUB_OUTPUT" not in environ.keys():
            DBM.p("Not in GitHub environment, not setting action output!")
            return
        prefix = "README stats current output:"
        eol = "".join(choice(ascii_letters) for _ in range(10))
        FM.write_file(environ["GITHUB_OUTPUT"], f"README_CONTENT<<{eol}\n{prefix}\n\n{stats}\n{eol}\n", append=True)
        DBM.g("Action output set!")
