import datetime
import time
import wikipedia

from typing import List

REQUESTS_PER_MINUTE = 100
LINKS_PER_PAGE = 200
MAX_SEARCH_COUNT = LINKS_PER_PAGE

wikipedia.set_lang("uk")
wikipedia.set_rate_limiting(
    rate_limit=True,
    min_wait=datetime.timedelta(seconds=1 / REQUESTS_PER_MINUTE * 60)
)


class WikiRacer:

    def find_path(self, start: str, finish: str) -> List[str]:
        visited = set()  # set to keep track of the visited articles
        queue = [(start, [start])]  # queue to keep track of the articles to be visited
        count = 0
        while queue:
            if count == MAX_SEARCH_COUNT:
                break
            count += 1
            current, path = queue.pop(0)  # dequeue the current article
            visited.add(current)  # mark it as visited
            try:
                links = wikipedia.page(current).links[:200]
            except wikipedia.exceptions.DisambiguationError as e:
                links = e.options[:200]
            except wikipedia.exceptions.PageError:
                # print(f"Error: {e}")
                continue

            for link in links:
                if link in visited:
                    continue
                if link == finish:
                    return path + [link]
                queue.append((link, path + [link]))
        return []


if __name__ == "__main__":
    timer_start = time.perf_counter()
    wr = WikiRacer()
    pth4 = wr.find_path('Дружба', 'Рим')
    print(pth4)
    # pth1 = wr.find_path('Марка (грошова одиниця)', 'Китайський календар')
    # print(pth1)
    # pth2 = wr.find_path('Фестиваль', 'Пілястра')
    # print(pth2)
    pth3 = wr.find_path('Дружина (військо)', '6 жовтня')
    print(pth3)

    timer_end = time.perf_counter()

    print("Elapsed:", timer_end - timer_start)
