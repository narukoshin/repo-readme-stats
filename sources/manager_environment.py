from os import getenv


class EnvironmentManager:
    _TRUTHY = ["true", "1", "t", "y", "yes"]

    GH_TOKEN = getenv("INPUT_GH_TOKEN")
    if not GH_TOKEN:
        raise KeyError("Missing required token: set INPUT_GH_TOKEN")

    REPO_OWNER = getenv("INPUT_REPO_OWNER", "").strip()
    REPO_NAME = getenv("INPUT_REPO_NAME", "").strip()

    SECTION_NAME = getenv("INPUT_SECTION_NAME", "repo_stats")
    PULL_BRANCH_NAME = getenv("INPUT_PULL_BRANCH_NAME", "")
    PUSH_BRANCH_NAME = getenv("INPUT_PUSH_BRANCH_NAME", "")

    SHOW_STARS = getenv("INPUT_SHOW_STARS", "True").lower() in _TRUTHY
    SHOW_FORKS = getenv("INPUT_SHOW_FORKS", "True").lower() in _TRUTHY
    SHOW_LANGUAGES = getenv("INPUT_SHOW_LANGUAGES", "True").lower() in _TRUTHY
    SHOW_COMMITS = getenv("INPUT_SHOW_COMMITS", "True").lower() in _TRUTHY
    SHOW_CONTRIBUTORS = getenv("INPUT_SHOW_CONTRIBUTORS", "True").lower() in _TRUTHY
    SHOW_RELEASES = getenv("INPUT_SHOW_RELEASES", "True").lower() in _TRUTHY
    SHOW_ISSUES = getenv("INPUT_SHOW_ISSUES", "True").lower() in _TRUTHY
    SHOW_PRS = getenv("INPUT_SHOW_PRS", "True").lower() in _TRUTHY
    SHOW_CLONES = getenv("INPUT_SHOW_CLONES", "False").lower() in _TRUTHY
    SHOW_TOPICS = getenv("INPUT_SHOW_TOPICS", "False").lower() in _TRUTHY

    COMMIT_BY_ME = getenv("INPUT_COMMIT_BY_ME", "False").lower() in _TRUTHY
    COMMIT_MESSAGE = getenv("INPUT_COMMIT_MESSAGE", "Updated with Repo Stats")
    COMMIT_USERNAME = getenv("INPUT_COMMIT_USERNAME", "")
    COMMIT_EMAIL = getenv("INPUT_COMMIT_EMAIL", "")
    COMMIT_SINGLE = getenv("INPUT_COMMIT_SINGLE", "").lower() in _TRUTHY
    FORCE_ADD = getenv("INPUT_FORCE_ADD", "false").lower() in _TRUTHY

    LOCALE = getenv("INPUT_LOCALE", "en")
    UPDATED_DATE_FORMAT = getenv("INPUT_UPDATED_DATE_FORMAT", "%d/%m/%Y %H:%M:%S")
    SYMBOL_VERSION = int(getenv("INPUT_SYMBOL_VERSION", "1"))
    BADGE_STYLE = getenv("BADGE_STYLE", "flat")

    DEBUG_LOGGING = getenv("INPUT_DEBUG_LOGGING", "0").lower() in _TRUTHY
    DEBUG_RUN = getenv("DEBUG_RUN", "False").lower() in _TRUTHY
