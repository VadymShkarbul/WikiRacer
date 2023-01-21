import datetime
import wikipedia

from typing import List

from db_config import DB

REQUESTS_PER_MINUTE = 100
LINKS_PER_PAGE = 200
MAX_SEARCH_COUNT = LINKS_PER_PAGE * 5


class WikiRacer:
    def __init__(self):
        self.db = DB()
        wikipedia.set_lang("uk")
        wikipedia.set_rate_limiting(
            rate_limit=True,
            min_wait=datetime.timedelta(seconds=1 / REQUESTS_PER_MINUTE * 60)
        )

    def find_path(self, start: str, finish: str) -> List[str]:
        # Create queue to keep track of the articles to be visited:
        queue = [(start, [start])]
        count = 0

        while queue:

            if count == MAX_SEARCH_COUNT:
                break
            count += 1
            # Dequeue the current article:
            current, path = queue.pop(0)
            # Getting current from DB:
            existing_page = self.db.get_page(current)
            # If current exists - take links that are on the page from the DB:
            if existing_page is not None:
                links = [link.name for link in existing_page.links]
            else:
                # Save page to DB in case it is not in DB
                new_page = self.db.add_page(current)
                # Using wikipedia module we take no more than
                # LINKS_PER_PAGE links from current page:
                try:
                    links = wikipedia.page(current).links[:LINKS_PER_PAGE]
                # Exception raised when a page resolves to a disambiguation page
                except wikipedia.exceptions.DisambiguationError as e:
                    # We choose links from options list:
                    links = e.options[:LINKS_PER_PAGE]
                # TODO: Rerequest if connection fails!
                # except requests.exceptions.ConnectionError:
                # If current page is empty - we skip it:
                except wikipedia.exceptions.PageError:
                    continue
                if links:
                    # Add current page links to DB:
                    self.db.add_links(new_page.id, links)

            # Finally check current page links:
            for link in links:
                if link == finish:
                    return path + [link]
                queue.append((link, path + [link]))
        return []
