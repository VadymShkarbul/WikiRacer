import time

import wikipedia
from typing import List

rpm = 100
links_per_page = 200
wikipedia.set_lang("uk")


class RateLimiter:
    def __init__(self, requests_per_minute):
        self.requests_per_minute = requests_per_minute
        self.last_request_time = time.time()

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            if time.time() - self.last_request_time < 60 / self.requests_per_minute:
                time.sleep(60 / self.requests_per_minute - (time.time() - self.last_request_time))
            self.last_request_time = time.time()
            return func(*args, **kwargs)

        return wrapper


rate_limiter = RateLimiter(rpm)


# def rate_limiter(requests_per_minute):
#     last_request_time = time.time()
#
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             nonlocal last_request_time
#             if time.time() - last_request_time < 60 / requests_per_minute:
#                 time.sleep(60 / requests_per_minute - (time.time() - last_request_time))
#             result = func(*args, **kwargs)
#             last_request_time = time.time()
#             return result
#
#         return wrapper
#
#     return decorator


class WikiRacer:
    @rate_limiter
    def find_path(self, start: str, finish: str) -> List[str]:

        visited = set()  # set to keep track of the visited articles
        queue = [(start, [start])]  # queue to keep track of the articles to be visited

        while queue:
            current, path = queue.pop(0)  # dequeue the current article
            visited.add(current)  # mark it as visited
            try:
                links = wikipedia.page(current).links[:200]
            except wikipedia.exceptions.DisambiguationError as e:
                links = e.options[:200]
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
    pth = wr.find_path('Дружба', 'Рим')
    print(pth)
    timer_end = time.perf_counter()

    print("Elapsed:", timer_end - timer_start)
