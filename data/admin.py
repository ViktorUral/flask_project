import sqlalchemy
from data.db_session import SqlAlchemyBase

class Admin(SqlAlchemyBase):
    __tablename__ = 'admin'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                          primary_key=True, autoincrement=True)
    password_hash = sqlalchemy.Column(sqlalchemy.String, nullable=True)