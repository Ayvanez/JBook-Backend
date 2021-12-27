import uuid
from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, Table, DateTime, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref

from app.db.base import Base


class User(Base):
    __tablename__ = 'user'
    __table_args__ = {"schema": "jbook"}

    uid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    first_name = Column(String(250), nullable=True)
    surname = Column(String(250), nullable=True)


class BookAuthor(Base):
    __tablename__ = 'book_author'
    __table_args__ = {"schema": "jbook"}

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String(50))


class BookPublisher(Base):
    __tablename__ = 'book_publisher'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String(50))


class BookCategory(Base):
    __tablename__ = 'book_category'
    __table_args__ = {"schema": "jbook"}

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String(50))
    popularity = Column(Integer)


class BookTag(Base):
    __tablename__ = 'book_tag'
    __table_args__ = {"schema": "jbook"}

    name = Column(String(50), primary_key=True, unique=True, nullable=False)


m2m_book_book_category = Table(
    '_m2m_book_book_category',
    Base.metadata,
    Column('book_id', ForeignKey('book.id'), primary_key=True),
    Column('category_id', ForeignKey('book_category.id'), primary_key=True),
    schema='jbook'
)

m2m_book_book_author = Table(
    '_m2m_book_book_author',
    Base.metadata,
    Column('book_id', ForeignKey('book.id'), primary_key=True),
    Column('book_author_id', ForeignKey('book_author.id'), primary_key=True),
    schema='jbook'
)

m2m_book_book_tag = Table(
    '_m2m_book_book_tag',
    Base.metadata,
    Column('book_id', ForeignKey('book.id'), primary_key=True),
    Column('book_tag', ForeignKey('book_tag.name'), primary_key=True),
    schema='jbook'
)


class BookImage(Base):
    __tablename__ = "book_image"
    __table_args__ = {"schema": "jbook"}

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    src = Column(String(400))
    book_id = Column(Integer, ForeignKey("book.id"))
    alt_text = Column(String(50))
    is_main = Column(Boolean)


class Book(Base):
    __tablename__ = 'book'
    __table_args__ = {"schema": "jbook"}

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    annotation = Column(Text, nullable=True)
    pub_date = Column(DateTime, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())

    publisher_id = Column(Integer, ForeignKey('book_publisher.id'))
    publisher = relationship(BookPublisher, backref="books")

    authors = relationship(BookAuthor, secondary=m2m_book_book_author, backref='books')
    categories = relationship(BookCategory, secondary=m2m_book_book_category, backref='books')
    tags = relationship(BookTag, secondary=m2m_book_book_tag, backref='books')
    images = relationship(BookImage, backref='books')
    book_rates = relationship('BookRate')


class BookComment(Base):
    __tablename__ = "book_comment"
    __table_args__ = {"schema": "jbook"}

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    book_id= Column(Integer, ForeignKey("book.id"))
    user_uid = Column(UUID(as_uuid=True), ForeignKey('user.uid'))
    user = relationship(User, backref='comments')
    pub_date = Column(TIMESTAMP, server_default=func.now())
    content = Column(Text)


class BookRate(Base):
    __tablename__ = "book_rate"
    __table_args__ = {"schema": "jbook"}

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    book_id = Column(Integer, ForeignKey("book.id"))
    user_uid = Column(UUID(as_uuid=True), ForeignKey('user.uid'))
    rate = Column(Integer)
    rated_at = Column(TIMESTAMP, server_default=func.now())


m2m_shelf_shelf_tag = Table(
    '_m2m_shelf_shelf_tag',
    Base.metadata,
    Column('shelf_uid', ForeignKey('shelf.uid'), primary_key=True),
    Column('shelf_tag', ForeignKey('shelf_tag.name'), primary_key=True),
    schema='jbook'
)

m2m_book_in_shelf_tag = Table(
    '_m2m_book_in_shelf_tag',
    Base.metadata,
    Column('book_in_shelf', ForeignKey('book_in_shelf.id'), primary_key=True),
    Column('book_in_shelf_tag_id', ForeignKey('book_in_shelf_tag.id'), primary_key=True),
    schema='jbook'
)


class ShelfImage(Base):
    __tablename__ = "shelf_image"
    __table_args__ = {"schema": "jbook"}

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    src = Column(String(400), unique=False)

    alt_text = Column(String(255), unique=False)


class ShelfTag(Base):
    __tablename__ = "shelf_tag"
    __table_args__ = {"schema": "jbook"}

    name = Column(String(50), primary_key=True, unique=True, nullable=False)


class BookInShelf(Base):
    __tablename__ = "book_in_shelf"
    __table_args__ = {"schema": "jbook"}

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    book_id = Column(Integer, ForeignKey("book.id"))
    shelf_uid = Column(UUID(as_uuid=True), ForeignKey('shelf.uid'), primary_key=True, default=uuid.uuid4)
    tags = relationship('BookInShelfTag', secondary=m2m_book_in_shelf_tag, lazy='joined')
    book = relationship(Book, lazy='joined')


class Shelf(Base):
    __tablename__ = "shelf"
    __table_args__ = {"schema": "jbook"}

    uid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String(20))

    avatar_id = Column(Integer, ForeignKey("shelf_image.id"))
    avatar = relationship(ShelfImage, backref="shelved")

    user_uid = Column(UUID(as_uuid=True), ForeignKey('user.uid'))
    user = relationship(User, backref="shelved", lazy="selectin")

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())

    tags = relationship(ShelfTag, secondary=m2m_shelf_shelf_tag, backref='shelves', lazy="selectin")

    books_in_shelf = relationship(BookInShelf, backref='shelf', lazy="selectin")


class ShelfRate(Base):
    __tablename__ = "shelf_rate"
    __table_args__ = {"schema": "jbook"}

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    user_uid = Column(UUID(as_uuid=True), ForeignKey('user.uid'), primary_key=True)
    shelf_uid = Column(UUID(as_uuid=True), ForeignKey('shelf.uid'), primary_key=True)
    rate = Column(Integer)


class BookInShelfTag(Base):
    __tablename__ = "book_in_shelf_tag"
    __table_args__ = {"schema": "jbook"}

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String(50))

class ShelfComment(Base):
    __tablename__ = "shelf_comment"
    __table_args__ = {"schema": "jbook"}

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    shelf_uid = Column(UUID(as_uuid=True), ForeignKey("shelf.uid"))
    user_uid = Column(UUID(as_uuid=True), ForeignKey('user.uid'))
    user = relationship(User, backref='shelf_comments')

    pub_date = Column(TIMESTAMP, server_default=func.now())
    content = Column(Text)


metadata = Base.metadata
