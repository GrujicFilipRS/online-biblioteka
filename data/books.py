import sqlalchemy
from datetime import datetime
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Book(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'books'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    uploaded_user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('user.id'), nullable=False)
    path = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now)

    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('author.id'), nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String)
    year = sqlalchemy.Column(sqlalchemy.Integer)
    grade = sqlalchemy.Column(sqlalchemy.Integer)
