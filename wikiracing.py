import datetime
import time

import psycopg2
import wikipedia

from typing import List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Page, Link

engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/postgres", echo=True, future=True)
Session = sessionmaker()
Session.configure(bind=engine)

session = Session()

REQUESTS_PER_MINUTE = 100
LINKS_PER_PAGE = 200
MAX_SEARCH_COUNT = LINKS_PER_PAGE

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

        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        # Check if the table links exists
        self.cursor.execute("SELECT to_regclass('page');")
        table_exists = self.cursor.fetchone()[0]
        if table_exists is None:
            self.cursor.execute(
                """
                    CREATE TABLE page (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL
                    );
                """
            )
            self.connection.commit()

        self.cursor.execute("SELECT to_regclass('link');")
        table_exists = self.cursor.fetchone()[0]
        if table_exists is None:
            self.cursor.execute(
                """
                    CREATE TABLE link (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    page_id integer REFERENCES page
                    );
                """
            )
            self.connection.commit()

    def insert_link(self, current):
        self.cursor.execute("INSERT INTO page (name) VALUES (%s)", (current,))
        self.connection.commit()

    def find_path(self, start: str, finish: str) -> List[str]:
        queue = [(start, [start])]  # queue to keep track of the articles to be visited
        count = 0

        while queue:
            if count == MAX_SEARCH_COUNT:
                break
            count += 1
            current, path = queue.pop(0)  # dequeue the current article
            # self.insert_link(current)
            # visited.add(current)  # mark it as visited
            existing_page = session.query(Page).filter_by(name=current).first()

            if existing_page is not None:
                links = [link.name for link in session.query(Link).filter_by(page_id=existing_page.id).all()]
            else:
                # save to DB
                new_page = Page(name=current)
                # TODO: page name has to be unique. See unique parameter in Column within models.py
                session.add(new_page)
                session.commit()

                try:
                    links = wikipedia.page(current).links[:LINKS_PER_PAGE]
                except wikipedia.exceptions.DisambiguationError as e:
                    links = e.options[:LINKS_PER_PAGE]
                except wikipedia.exceptions.PageError:
                    continue

                if links:
                    for link_name in links:
                        new_link = Link(page_id=new_page.id, name=link_name)
                        session.add(new_link)
                    session.commit()

            for link in links:
                if link == finish:
                    return path + [link]
                queue.append((link, path + [link]))
        return []


if __name__ == "__main__":
    # page = Page(name='my_page')
    # session.add(page)
    # session.commit()
    # link = Link(name='test_link', page_id=page.id)
    #
    # session.add(link)
    # session.commit()
    #
    # links_by_page = session.query(Link).join(Page, Page.id == Link.page_id).all()

    timer_start = time.perf_counter()
    wr = WikiRacer()
    # pth4 = wr.find_path('Дружба', 'Рим')
    # print(pth4)
    pth1 = wr.find_path('Марка (грошова одиниця)', 'Китайський календар')
    print(pth1)
    # pth2 = wr.find_path('Фестиваль', 'Пілястра')
    # print(pth2)
    # pth3 = wr.find_path('Дружина (військо)', '6 жовтня')
    # print(pth3)

    timer_end = time.perf_counter()

    print("Elapsed:", timer_end - timer_start)
