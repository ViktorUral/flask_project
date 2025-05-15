import sqlalchemy
from data.db_session import SqlAlchemyBase

class Map(SqlAlchemyBase):
    __tablename__ = 'maps'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                          primary_key=True, autoincrement=True)
    city = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    zoom = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    image_data = sqlalchemy.Column(sqlalchemy.LargeBinary, nullable=True)