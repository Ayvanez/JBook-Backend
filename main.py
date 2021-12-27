import asyncio

from sqlalchemy import Column, event, create_engine, text
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import declarative_base, joinedload, Session
from sqlalchemy.orm import relationship
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import sessionmaker

from app.db.queries import tables as models

engine = create_engine(
    'postgresql://postgres:1@localhost/jbook'
)

categories = ['cat1', '1']
authors = ['aut3']
publishers = [None]
user_id = 4

user_rate_query = select(models.BookRate.book_id, models.BookRate.rate.label('userRate')) \
    .filter(models.BookRate.user_id == user_id).cte()

rate_query = select(models.BookRate.book_id, func.avg(models.BookRate.rate).label('rate')) \
    .group_by(models.BookRate.book_id).cte()

query = select(models.Book, rate_query.c.rate, user_rate_query.c.userRate) \
    .options(
    selectinload(models.Book.categories),
    selectinload(models.Book.authors),
    selectinload(models.Book.publisher),
    selectinload(models.Book.tags),
    selectinload(models.Book.images),
)

# query = query.filter(models.Book.categories.any(models.BookCategory.name.in_(categories)))
# query = query.filter(models.Book.authors.any(models.BookAuthor.name.in_(authors)))
# query = query.filter(models.Book.publisher.has(models.BookPublisher.name.in_(publishers)))
query = query.outerjoin(user_rate_query)
query = query.outerjoin(rate_query)
query = query.order_by(text('rate asc')).limit(2).offset(0)
print(query.compile(engine))

with Session(engine) as session:
    ob = session.execute(query).all()
    print(ob)
    session.commit()