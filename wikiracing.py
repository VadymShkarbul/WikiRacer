import datetime
import time

import psycopg2
import psycopg2.extensions
import wikipedia


from typing import List

REQUESTS_PER_MINUTE = 100
LINKS_PER_PAGE = 200
wikipedia.set_lang("uk")
wikipedia.set_rate_limiting(
    rate_limit=True,
    min_wait=datetime.timedelta(seconds=1 / REQUESTS_PER_MINUTE * 60)
)


class WikiRacer:
    def __init__(self):
        self.connection = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="postgres",
        )

        # Set the connection encoding to UTF8
        self.connection.set_client_encoding('UTF8')
        self.cursor = self.connection.cursor()
        self.check_create_table()

    def check_create_table(self):
        # Check if the table links exists
        self.cursor.execute("SELECT to_regclass('links');")
        table_exists = self.cursor.fetchone()[0]
        if table_exists is None:
            self.cursor.execute(
                """
                CREATE TABLE links (
                    id SERIAL PRIMARY KEY,
                    source TEXT NOT NULL,
                    target TEXT NOT NULL
                );
                """
            )
            self.connection.commit()

        self.cursor.execute("SELECT to_regclass('results');")
        table_exists = self.cursor.fetchone()[0]
        if table_exists is None:
            self.cursor.execute(
                """
                CREATE TABLE results     (
                    id SERIAL PRIMARY KEY,
                    start TEXT NOT NULL,
                    finish TEXT NOT NULL,
                    result TEXT NOT NULL
                );
                """
            )
            self.connection.commit()

    def check_link(self, source):
        self.cursor.execute("SELECT target FROM links WHERE source = %s", (source,))
        target = self.cursor.fetchone()
        if target:
            return target[0]

    def insert_link(self, current, link):
        self.cursor.execute("INSERT INTO links (source, target) VALUES (%s, %s)", (current, link))
        self.connection.commit()

    def check_result(self, start, finish):
        self.cursor.execute("SELECT result FROM results WHERE start = %s AND finish = %s", (start, finish))
        result = self.cursor.fetchone()
        if result:
            return result

    def insert_result(self, start, finish, result):
        self.cursor.execute("INSERT INTO results (start, finish, result) VALUES (%s, %s, %s)", (start, finish, result))
        self.connection.commit()

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
    pth1 = wr.find_path('Дружба', 'Рим')
    print(pth1)
    pth2 = wr.find_path('Мітохондріальна ДНК', 'Вітамін K')
    print(pth2)
    timer_end = time.perf_counter()

    print("Elapsed:", timer_end - timer_start)
