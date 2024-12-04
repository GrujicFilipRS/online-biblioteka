import sqlalchemy

from data.db_session import SqlAlchemyBase, create_session
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Author(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'author'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.String, default="https://t4.ftcdn.net/jpg/04/70/29/97/360_F_470299797_UD0eoVMMSUbHCcNJCdv2t8B2g1GVqYgs.jpg")
