import sqlalchemy
from datetime import datetime
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Book(SqlAlchemyBase):
    __tablename__ = 'books'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    uploaded_user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('user.id'), nullable=False)
    path = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now)

    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('author.id'), nullable=False)
    author = sqlalchemy.orm.relationship('Author')

    description = sqlalchemy.Column(sqlalchemy.String)
    year = sqlalchemy.Column(sqlalchemy.Integer)
    grade = sqlalchemy.Column(sqlalchemy.Integer)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author.to_dict(),
            "description": self.description,
            "year": self.year,
            "grade": self.grade,
            "uploaded_user_id": self.uploaded_user_id,
            "path": self.path,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
