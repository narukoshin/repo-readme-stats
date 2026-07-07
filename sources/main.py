"""
Repo Readme Stats — dynamically generated repo metrics for your README.
"""

from asyncio import run
from datetime import datetime
from humanize import intword, intcomma

from manager_download import init_download_manager, DownloadManager as DM
from manager_environment import EnvironmentManager as EM
from manager_github import init_github_manager, GitHubManager as GHM
from manager_file import init_localization_manager, FileManager as FM
from manager_debug import init_debug_manager, DebugManager as DBM
from graphics_list_formatter import make_list, make_graph


def fmt_count(n: int) -> str:
    if n >= 1000:
        return intword(n)
    return str(n)


async def get_repo_stats() -> str:
    DBM.i("Fetching repo stats...")
    stats = str()
    data = await DM.fetch_repo_stats(EM.REPO_OWNER, EM.REPO_NAME)
    repo = data.get("repo") or {}

    if EM.SHOW_STARS:
        DBM.i("Adding star info...")
        stargazers = repo.get("stargazers_count", 0)
        stats += f"⭐ **Stars** \n\n```text\n{FM.t('Total')}: {fmt_count(stargazers)}\n```\n\n"

    if EM.SHOW_FORKS:
        DBM.i("Adding fork info...")
        forks = repo.get("forks_count", 0)
        stats += f"🍴 **Forks** \n\n```text\n{FM.t('Total')}: {fmt_count(forks)}\n```\n\n"

    if EM.SHOW_ISSUES:
        DBM.i("Adding issue info...")
        open_issues = data.get("open_issues", 0)
        stats += f"📋 **Issues** \n\n```text\n{FM.t('Open')}: {open_issues}\n```\n\n"

    if EM.SHOW_PRS:
        DBM.i("Adding PR info...")
        prs = data.get("open_prs", 0)
        stats += f"🔀 **Pull Requests** \n\n```text\n{FM.t('Open')}: {prs}\n```\n\n"

    if EM.SHOW_LANGUAGES:
        DBM.i("Adding language breakdown...")
        langs = data.get("languages", {})
        if langs:
            total = sum(langs.values())
            lang_data = []
            for name, bytes_count in sorted(langs.items(), key=lambda x: x[1], reverse=True):
                pct = (bytes_count / total) * 100
                lang_data.append({"name": name, "text": f"{pct:.1f}%", "percent": pct})
            stats += f"💬 **{FM.t('Languages')}** \n\n```text\n{make_list(data=lang_data)}\n```\n\n"

    if EM.SHOW_CONTRIBUTORS:
        DBM.i("Adding contributor info...")
        contribs = data.get("contributors", [])
        if contribs:
            names = []
            texts = []
            percents = []
            total_contribs = sum(c.get("contributions", 0) for c in contribs)
            for c in contribs:
                names.append(c.get("login", "?"))
                texts.append(f"{c.get('contributions', 0)} commits")
                percents.append((c.get("contributions", 0) / total_contribs * 100) if total_contribs else 0)
            stats += f"👥 **{FM.t('Top Contributors')}** \n\n```text\n{make_list(names=names, texts=texts, percents=percents)}\n```\n\n"

    if EM.SHOW_COMMITS:
        DBM.i("Adding recent commit info...")
        commits = data.get("recent_commits", [])
        if commits:
            d_names = []
            for c in commits:
                c_data = c.get("commit", {})
                author = c_data.get("author", {})
                name = author.get("name", "?")[:20]
                msg = c_data.get("message", "").split("\n")[0][:30]
                d_names.append(f"{name}: {msg}")
            per_commit = 100.0 / len(commits) if commits else 0
            texts_data = [f"commit {i+1}" for i in range(len(commits))]
            percents_data = [per_commit for _ in commits]
            stats += f"🕐 **{FM.t('Recent Commits')}** \n\n```text\n{make_list(names=d_names, texts=texts_data, percents=percents_data, sort=False)}\n```\n\n"

    if EM.SHOW_RELEASES:
        DBM.i("Adding release info...")
        release = data.get("latest_release")
        if release:
            tag = release.get("tag_name", "?")
            name = release.get("name", "") or ""
            published = release.get("published_at", "")[:10]
            stats += f"🏷 **{FM.t('Latest Release')}** \n\n```text\n{tag} {name}\n📅 {published}\n```\n\n"

    DBM.g("Repo stats collected!")
    return stats


async def main():
    init_github_manager()
    await init_download_manager()
    init_localization_manager()
    DBM.i("Managers initialized.")

    stats = await get_repo_stats()
    if not EM.DEBUG_RUN:
        GHM.update_readme(stats)
        GHM.commit_update()
    else:
        GHM.set_github_output(stats)
    await DM.close_remote_resources()


if __name__ == "__main__":
    init_debug_manager()
    start_time = datetime.now()
    DBM.g("Program execution started at $date.", date=start_time)
    run(main())
    end_time = datetime.now()
    DBM.g("Program execution finished at $date.", date=end_time)
    DBM.p("Program finished in $time.", time=end_time - start_time)
