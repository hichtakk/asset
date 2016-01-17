import datetime

from sqlalchemy import (
    Column,
    Index,
    Integer,
    String,
    ForeignKey,
    UniqueConstraint
    )

from sqlalchemy.types import (
    Date,
    Enum
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref
    )

from pyramid.security import (
    Allow,
    Everyone
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


#class MyModel(Base):
#    __tablename__ = 'models'
#    id = Column(Integer, primary_key=True)
#    name = Column(String(32))
#    value = Column(Integer)

#Index('my_index', MyModel.name, unique=True, mysql_length=255)


class RootFactory(object):
    __acl__ = [(Allow, Everyone, 'view'),
               (Allow, 'group:editors', 'edit')]

    def __init__(self, request):
        pass


class Maker(Base):
    __tablename__ = 'maker'
    id = Column(Integer, primary_key=True)
    name = Column(String(32), unique=True)
    description = Column(String(256))

    models = relationship('Model', back_populates='maker')


class Vendor(Base):
    __tablename__ = 'vendor'
    id = Column(Integer, primary_key=True)
    name = Column(String(32), unique=True)
    email = Column(String(128))
    description = Column(String(256))

    items = relationship('Item', back_populates='vendor')


class Model(Base):
    __tablename__ = 'model'
    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    maker_id = Column(Integer, ForeignKey('maker.id'))
    description = Column(String(256))

    maker = relationship('Maker', back_populates='models')
    items = relationship('Item', back_populates='model')
    __table__args__ = (UniqueConstraint('name', 'maker_id', '_name_maker_uc'))


class Location(Base):
    __tablename__ = 'location'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True)
    description = Column(String(256))
    items = relationship('Item', back_populates='location')


class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    serial = Column(String(64), nullable=False, unique=True)
    model_id = Column(Integer, ForeignKey('model.id'), nullable=False)
    vendor_id = Column(Integer, ForeignKey('vendor.id'), nullable=False)
    installed_id = Column(Integer, ForeignKey('item.id'))
    installed_description = Column(String(32))
    support = Column(Enum('None', 'on site', 'send back'), nullable=False)
    support_end = Column(Date, default=datetime.datetime.now)
    status = Column(Enum('in stock', 'in use', 'disposed'), nullable=False)
    location_id = Column(Integer, ForeignKey('location.id'), nullable=False)
    asset_number = Column(String(10))
    settlement_number = Column(String(10))
    delivery_date = Column(Date, default=datetime.datetime.now)
    description = Column(String(256))
    updated_at = Column(Date, onupdate=datetime.datetime.now)
    #last_updated_by_id = Column(Integer, ForeignKey('user.id'))

    model = relationship('Model', back_populates='items')
    vendor = relationship('Vendor', back_populates='items')
    location = relationship('Location', back_populates='items')
    attachments = relationship(
        'Item',
        backref=backref('parent', remote_side=[id])
    )


