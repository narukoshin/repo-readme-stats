# repo-readme-stats

stick this in your readme and watch it come alive. stars, forks, languages, recent commits, top contributors, latest release — all fresh from github's api, rendered with those old-school progress bars you either love or hate.

## what is this

a fork of [anmol098/waka-readme-stats](https://github.com/anmol098/waka-readme-stats) that swaps wakatime personal stats for github repo data. same visual engine (██░░ bars, emoji headers, percentages), different data source. we kept what worked and replaced the rest.

## usage

drop these markers into your readme:

```markdown
<!--START_SECTION:repo_stats-->
<!--END_SECTION:repo_stats-->
```

create `.github/workflows/repo-stats.yml`:

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
      - uses: narukoshin/repo-readme-stats@main
        with:
          GH_TOKEN: ${{ secrets.GH_TOKEN }}
          REPO_OWNER: your-org
          REPO_NAME: your-repo
```

## inputs

| input | default | description |
|-------|---------|-------------|
| `GH_TOKEN` | `${{ github.token }}` | token with repo scope |
| `REPO_OWNER` | — | repo owner (required) |
| `REPO_NAME` | — | repo name (required) |
| `SECTION_NAME` | `repo_stats` | marker name in readme |
| `SHOW_STARS` | `True` | star count |
| `SHOW_FORKS` | `True` | fork count |
| `SHOW_LANGUAGES` | `True` | language breakdown |
| `SHOW_COMMITS` | `True` | recent commits |
| `SHOW_CONTRIBUTORS` | `True` | top contributors |
| `SHOW_RELEASES` | `True` | latest release |
| `SHOW_ISSUES` | `True` | open issues |
| `SHOW_PRS` | `True` | open pull requests |
| `LOCALE` | `en` | translation locale |
| `SYMBOL_VERSION` | `1` | progress bar style |
| `COMMIT_MESSAGE` | `Updated with Repo Stats` | commit message |
| `COMMIT_BY_ME` | `False` | commit as repo owner |

## how it works

1. action runs on cron or manual trigger
2. docker container starts, hits the github rest api
3. stats get formatted into text progress bars
4. clones the repo, injects between `START_SECTION` / `END_SECTION`
5. commits and pushes. done.

## credits

- **original**: [anmol098/waka-readme-stats](https://github.com/anmol098/waka-readme-stats) — the template we forked from
- **fork**: reimplemented by [AIRI/Eluuna](https://github.com/airi461) for narukoshin
