from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Page, Link


class DB:
    def __init__(self):
        self.engine = create_engine(
            "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres",
            echo=True,
            future=True
        )
        Session = sessionmaker()
        Session.configure(bind=self.engine)
        self.session = Session()

    def add_page(self, name):
        new_page = Page(name=name)
        self.session.add(new_page)
        self.session.commit()
        return new_page

    def get_page(self, name):
        return self.session.query(Page).filter_by(name=name).first()

    def add_links(self, page_id: int, links: List[str]) -> None:
        for link in links:
            link = Link(page_id=page_id, name=link)
            self.session.add(link)
        self.session.commit()
