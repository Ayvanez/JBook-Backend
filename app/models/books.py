from sqlalchemy import Column, Integer, String, Sequence, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.testing.schema import Table

from app.db.base import Base

book_sequence = Sequence('book_id_seq', start=1, metadata=Base.metadata)
category_sequence = Sequence('category_id_seq', start=1, metadata=Base.metadata)
publisher_sequence = Sequence('publisher_id_seq', start=1, metadata=Base.metadata)
author_sequence = Sequence('author_id_seq', start=1, metadata=Base.metadata)

m2m_book_book_category = Table(
    '_m2m_book_book_category',
    Base.metadata,
    Column('book_id', ForeignKey('book.id'), primary_key=True),
    Column('category_id', ForeignKey('book_category.id'), primary_key=True)
)

m2m_book_book_author = Table(
    '_m2m_book_book_author',
    Base.metadata,
    Column('book_id', ForeignKey('book.id'), primary_key=True),
    Column('book_author', ForeignKey('book_author.id'), primary_key=True)
)


class BookAuthor(Base):
    __tablename__ = 'book_author'
    id = Column(Integer, author_sequence, primary_key=True, autoincrement=True, unique=True,
                server_default=author_sequence.next_value())
    name = Column(String(50))


class PublishingHouse(Base):
    __tablename__ = 'publishing_house'
    id = Column(Integer, publisher_sequence, primary_key=True, autoincrement=True, unique=True,
                server_default=publisher_sequence.next_value())
    name = Column(String(50))


class BookCategory(Base):
    __tablename__ = 'book_category'
    id = Column(Integer, category_sequence, primary_key=True, autoincrement=True, unique=True,
                server_default=category_sequence.next_value())
    name = Column(String(50))


class Book(Base):
    __tablename__ = 'book'
    id = Column(Integer, book_sequence, primary_key=True, autoincrement=True, server_default=book_sequence.next_value(),
                unique=True, )
    title = Column(String(100), nullable=False)
    description = Column(String(1000), nullable=True)

    publisher_id = Column(Integer, ForeignKey('publishing_house.id'))
    publisher = relationship("PublishingHouse", backref="books")

    authors = relationship('BookAuthor', secondary=m2m_book_book_author, backref='books')
    categories = relationship('BookCategory', secondary=m2m_book_book_category, backref='books')
