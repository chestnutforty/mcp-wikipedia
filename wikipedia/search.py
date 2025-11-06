import os
import asyncio
import pandas as pd
import wikitextparser as wtp

from datetime import datetime, timezone
from httpx import AsyncClient
from dataclasses import dataclass, asdict

@dataclass
class WikiQueryRequest:
    srsearch: str # search query
    srlimit: int = 2
    srnamespace: int = 0
    action: str = 'query'
    format: str = 'json'
    formatversion: int = 2
    list: str = 'search'
    maxlag: int = 5
    redirects: int = 1


@dataclass
class WikiRevisionRequest:
    pageids: int
    rvstart: str # iso
    action: str = "query"
    format: str = "json"
    formatversion: int = 2
    prop: str = "revisions"
    rvlimit: int = 1
    rvdir: str = 'older'
    rvprop: str = "ids|timestamp|content"
    rvslots: str = "main"
    maxlag: int = 5

@dataclass
class WikiRevisionResponse:
    pageid: int
    title: str
    oldid: int
    timestamp: str
    content: str

class Wikipedia:
    def __init__(
        self,
        lang: str = 'en',
        limit: int = 2,
        save_dir: str = None,
        remove_wikitext: bool = True,
        debug: bool = False,
        access_token: str = os.getenv("WIKIPEDIA_ACCESS_TOKEN")
    ):
        self.lang = lang
        self.limit = limit
        self.remove_wikitext = remove_wikitext
        self.api_endpoint = f'https://{lang}.wikipedia.org/w/api.php'
        self.save_dir = save_dir
        self.access_token = access_token

        if self.save_dir is None:
            self.save_dir = os.path.join('data', 'wikipedia_revisions')

    async def search(self, query: str, end_date: datetime):
        async with AsyncClient() as client:
            page_ids = await self._get_wiki_search(query, client)
            revisions = await self._get_wiki_revisions(page_ids, end_date, client)

        return revisions

    async def _get_wiki_search(self, query, client):
        headers = {}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"

        r = await client.get(
            self.api_endpoint,
            params=self._prepare_search_payload(query),
            headers=headers
        )

        r.raise_for_status()
        page_ids = [hit["pageid"] for hit in r.json().get("query", {}).get("search", [])]
        return page_ids

    async def _get_wiki_revisions(self, page_ids, end_date, client):
        headers = {}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"

        all_pages = []
        for page in page_ids:
            r = await client.get(
                self.api_endpoint,
                params=self._prepare_revision_payload(
                    page,
                    self._format_timestamp(end_date)
                ),
                headers=headers
            )
            r.raise_for_status()
            pages = r.json().get("query", {}).get("pages", [])

            if not pages:
                continue
            p = pages[0]

            revs = p.get("revisions", [])
            if not revs:
                continue
            rev = revs[0]
            wikitext = (rev.get("slots") or {}).get("main", {}).get("content")

            # Strip leading and trailing whitespace
            if wikitext:
                wikitext = wikitext.strip()

            all_pages.append(
                asdict(
                    WikiRevisionResponse(
                        pageid=p['pageid'],
                        title=p['title'],
                        oldid=rev['revid'],
                        timestamp=rev['timestamp'],
                        content=wtp.remove_markup(wikitext).strip() if self.remove_wikitext else wikitext
                    )
                )
            )

        return all_pages

    def _save_dataframe(self, pages):
        pages = pd.DataFrame(pages)

    def _prepare_search_payload(self, query):
        return asdict(WikiQueryRequest(srsearch=query, srlimit=self.limit))

    def _prepare_revision_payload(self, page_id, cutoff_date):
        return asdict(WikiRevisionRequest(page_id, cutoff_date))

    @staticmethod
    def _format_timestamp(dt: datetime):
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)  # assume UTC if naive
        else:
            dt = dt.astimezone(timezone.utc)      # convert to UTC
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    def save_results(self):
        # idk maybe at some point we want to save tool outputs here also idk.
        pass


if __name__ == "__main__":
    w = Wikipedia('ru')
    out = asyncio.run(w.search('деньги', datetime(2023,1,1)))
    print(out)
