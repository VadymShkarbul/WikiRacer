from sqlalchemy import String, Column, Integer, ForeignKey
from sqlalchemy.orm import declarative_base

base = declarative_base()
metadata = base.metadata


class Page(base):
    __tablename__ = 'page'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))


class Link(base):
    __tablename__ = 'link'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    page_id = Column(Integer, ForeignKey("page.id"), nullable=False)
