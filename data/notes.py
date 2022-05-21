import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
import datetime


class Notes(SqlAlchemyBase):
    __tablename__ = 'Notes'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.Text)
    content = sqlalchemy.Column(sqlalchemy.Text)
    date = sqlalchemy.Column(sqlalchemy.Text,
                             default=datetime.datetime.now().date())