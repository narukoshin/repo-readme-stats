import asyncio
import collections.abc
import json
from hashlib import md5
from string import Template
from typing import Any, Callable, Optional, List, Tuple

from httpx import AsyncClient

from manager_environment import EnvironmentManager as EM
from manager_debug import DebugManager as DBM

GITHUB_API_QUERIES = {
    "repo_branch_list": """
{
    repository(owner: "$owner", name: "$name") {
        refs(refPrefix: "refs/heads/", orderBy: {direction: DESC, field: TAG_COMMIT_DATE}, $pagination) {
            nodes {
                name
            }
            pageInfo {
                endCursor
                hasNextPage
            }
        }
    }
}
""",
    "repo_commit_list": """
{
    repository(owner: "$owner", name: "$name") {
        ref(qualifiedName: "refs/heads/$branch") {
            target {
                ... on Commit {
                    history(author: { id: "$id" }, $pagination) {
                        nodes {
                            ... on Commit {
                                committedDate
                                oid
                            }
                        }
                        pageInfo {
                            endCursor
                            hasNextPage
                        }
                    }
                }
            }
        }
    }
}
""",
}


async def init_download_manager():
    pass


class DownloadManager:

    _client = AsyncClient(timeout=60.0)
    _REMOTE_RESOURCES_CACHE = dict()

    @staticmethod
    async def close_remote_resources():
        for resource in DownloadManager._REMOTE_RESOURCES_CACHE.values():
            if isinstance(resource, asyncio.Task):
                resource.cancel()
                try:
                    await resource
                except asyncio.CancelledError:
                    pass
                except Exception:
                    pass
            elif isinstance(resource, collections.abc.Awaitable):
                try:
                    await resource
                except Exception:
                    pass

    @staticmethod
    async def _fetch_graphql_query(query: str, retries_count: int = 10, **kwargs) -> dict:
        headers = {"Authorization": f"Bearer {EM.GH_TOKEN}"}
        res = await DownloadManager._client.post(
            "https://api.github.com/graphql",
            json={"query": Template(GITHUB_API_QUERIES[query]).substitute(kwargs)},
            headers=headers,
        )
        if res.status_code == 200:
            return res.json()
        if res.status_code in (502, 503, 504, 429, 403) and retries_count > 0:
            await asyncio.sleep(1.0)
            return await DownloadManager._fetch_graphql_query(query, retries_count - 1, **kwargs)
        try:
            body_preview = json.dumps(res.json())[:500]
        except (json.JSONDecodeError, ValueError):
            body_preview = (res.text or "").replace("\n", " ").replace("\r", " ")[:500]
        raise Exception(
            f"Query '{query}' failed (HTTP {res.status_code}). Body: {body_preview}"
        )

    @staticmethod
    def _find_pagination_and_data_list(response: dict) -> Tuple[List, dict]:
        if "nodes" in response.keys() and "pageInfo" in response.keys():
            return response["nodes"], response["pageInfo"]
        elif len(response) == 1 and isinstance(response[list(response.keys())[0]], dict):
            return DownloadManager._find_pagination_and_data_list(response[list(response.keys())[0]])
        else:
            return list(), dict(hasNextPage=False)

    @staticmethod
    async def _fetch_graphql_paginated(query: str, max_nodes: Optional[int] = None, **kwargs) -> List[dict]:
        initial = await DownloadManager._fetch_graphql_query(query, **kwargs, pagination="first: 100")
        page_list, page_info = DownloadManager._find_pagination_and_data_list(initial)
        if max_nodes and len(page_list) >= max_nodes:
            return page_list[:max_nodes]
        while page_info["hasNextPage"] and (max_nodes is None or len(page_list) < max_nodes):
            pagination = f'first: 100, after: "{page_info["endCursor"]}"'
            resp = await DownloadManager._fetch_graphql_query(query, **kwargs, pagination=pagination)
            new_list, page_info = DownloadManager._find_pagination_and_data_list(resp)
            page_list += new_list
            if max_nodes and len(page_list) >= max_nodes:
                page_list = page_list[:max_nodes]
                break
        return page_list

    @staticmethod
    async def get_remote_graphql(query: str, **kwargs) -> Any:
        max_nodes = kwargs.pop("_max_nodes", None)
        cache_key = f"{query}_{md5(json.dumps(kwargs, sort_keys=True).encode('utf-8')).hexdigest()}"
        if cache_key not in DownloadManager._REMOTE_RESOURCES_CACHE:
            if "$pagination" in GITHUB_API_QUERIES[query]:
                res = await DownloadManager._fetch_graphql_paginated(query, max_nodes=max_nodes, **kwargs)
            else:
                res = await DownloadManager._fetch_graphql_query(query, **kwargs)
            DownloadManager._REMOTE_RESOURCES_CACHE[cache_key] = res
        else:
            res = DownloadManager._REMOTE_RESOURCES_CACHE[cache_key]
        return res

    @staticmethod
    async def fetch_rest_json(url: str) -> Optional[dict]:
        headers = {"Authorization": f"Bearer {EM.GH_TOKEN}", "Accept": "application/vnd.github.v3+json"}
        res = await DownloadManager._client.get(url, headers=headers)
        if res.status_code == 200:
            return res.json()
        DBM.w(f"REST query failed ({url}): HTTP {res.status_code}")
        return None

    @staticmethod
    async def fetch_repo_stats(owner: str, repo: str) -> dict:
        base = f"https://api.github.com/repos/{owner}/{repo}"
        stats = {}

        repo_data = await DownloadManager.fetch_rest_json(base)
        if repo_data:
            stats["repo"] = repo_data

        languages = await DownloadManager.fetch_rest_json(f"{base}/languages")
        if languages:
            stats["languages"] = languages

        commits = await DownloadManager.fetch_rest_json(f"{base}/commits?per_page=10")
        if commits:
            stats["recent_commits"] = commits

        contributors = await DownloadManager.fetch_rest_json(f"{base}/contributors?per_page=5")
        if contributors:
            stats["contributors"] = contributors

        releases = await DownloadManager.fetch_rest_json(f"{base}/releases/latest")
        if releases:
            stats["latest_release"] = releases

        issue_search = await DownloadManager.fetch_rest_json(
            f"https://api.github.com/search/issues?q=repo:{owner}/{repo}+type:issue+state:open"
        )
        if issue_search:
            stats["open_issues"] = issue_search.get("total_count", 0)

        pr_search = await DownloadManager.fetch_rest_json(
            f"https://api.github.com/search/issues?q=repo:{owner}/{repo}+type:pr+state:open"
        )
        if pr_search:
            stats["open_prs"] = pr_search.get("total_count", 0)

        return stats
