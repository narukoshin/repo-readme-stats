# 📊 Repo Readme Stats

Dynamically generated repo metrics for your GitHub README — stars, forks, languages, commits, contributors, releases, issues, and pull requests.

Forked and reimplemented from [anmol098/waka-readme-stats](https://github.com/anmol098/waka-readme-stats).  
We kept the visual engine (progress bars, emoji headers, percentage formatting) and replaced the data source from WakaTime personal coding stats with GitHub Repository API data.

## Usage

Add a comment marker to your `README.md` where you want the stats to appear:

```markdown
<!--START_SECTION:repo_stats-->
<!--END_SECTION:repo_stats-->
```

Create `.github/workflows/repo-stats.yml`:

```yaml
name: Repo Stats

on:
  schedule:
    - cron: '30 18 * * *'
  workflow_dispatch:

jobs:
  update-readme:
    runs-on: ubuntu-latest
    steps:
      - uses: THERXWOLD/repo-readme-stats@main
        with:
          GH_TOKEN: ${{ secrets.GH_TOKEN }}
          REPO_OWNER: THERXWOLD
          REPO_NAME: my-repo
```

## Inputs

| Input | Default | Description |
|-------|---------|-------------|
| `GH_TOKEN` | `${{ github.token }}` | GitHub token with repo scope |
| `REPO_OWNER` | — | Repository owner (required) |
| `REPO_NAME` | — | Repository name (required) |
| `SECTION_NAME` | `repo_stats` | Marker name in README |
| `SHOW_STARS` | `True` | Star count |
| `SHOW_FORKS` | `True` | Fork count |
| `SHOW_LANGUAGES` | `True` | Language breakdown |
| `SHOW_COMMITS` | `True` | Recent commits |
| `SHOW_CONTRIBUTORS` | `True` | Top contributors |
| `SHOW_RELEASES` | `True` | Latest release info |
| `SHOW_ISSUES` | `True` | Open issue count |
| `SHOW_PRS` | `True` | Open PR count |
| `LOCALE` | `en` | Translation locale |
| `SYMBOL_VERSION` | `1` | Progress bar symbol version |
| `COMMIT_MESSAGE` | `Updated with Repo Stats` | Git commit message |
| `COMMIT_BY_ME` | `False` | Commit as the repo owner |
| `PULL_BRANCH_NAME` | `""` | Branch to read README from |
| `PUSH_BRANCH_NAME` | `""` | Branch to write README to |

## How It Works

1. GitHub Action runs on cron or manual trigger
2. Docker container starts and calls the GitHub REST API to fetch repo stats
3. Stats are formatted using text progress bars (the same visual engine from waka-readme-stats)
4. The container clones the target repo, injects formatted stats between `<!--START_SECTION:repo_stats-->` / `<!--END_SECTION:repo_stats-->` markers
5. Commits and pushes the updated README

## Credits

- **Original**: [Anmol Pratap Singh](https://github.com/anmol098) — [waka-readme-stats](https://github.com/anmol098/waka-readme-stats)
- **Fork**: Reimplemented by AIRI for [therXwold](https://github.com/THERXWOLD)
