from sqlalchemy.sql.sqltypes import Boolean, DateTime
from database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, ForeignKey, String


class InstagramImage(Base):
    __tablename__ = 'images'
    id = Column(Integer(), primary_key=True)
    user_id = Column('user_id', Integer(), ForeignKey('user.id'))
    user = relationship("User", back_populates="images")
    image_url = Column(String(), nullable=False)
    publish_date = Column(DateTime(), nullable=False)
    published = Column(Boolean, default=False)
