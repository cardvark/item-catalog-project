from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import asc, desc


Base = declarative_base()

engine = create_engine('sqlite:///gamescatalog.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# User functions
def create_user(login_session):
    new_user = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture']
        )

    session.add(new_user)
    session.commit()
    return new_user.id


def get_user(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def get_user_id(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(250))
    picture = Column(String)


# Category functions
def create_category(name):
    new_category = Category(name=name)
    session.add(new_category)
    session.commit()
    return new_category.id


def get_cat(cat_id):
    cat = session.query(Category).filter_by(id=cat_id).one()
    return cat


def get_cat_id(name):
    cat = session.query(Category).filter_by(name=name).one()
    return cat.id


def get_items_in_category(category_id):
    items_list = session.query(ItemTitle).join(ItemTitle.category).filter_by(id=category_id)
    return items_list


def get_all_categories():
    categories = session.query(Category).order_by(asc(Category.name))
    return categories


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name
        }


# ItemTitle functions
def create_item(name, description, category_id, user_id):
    new_item = ItemTitle(
        name=name,
        description=description,
        category_id=category_id,
        user_id=user_id
        )
    session.add(new_item)
    session.commit()
    return new_item


def get_item(item_id):
    item = session.query(ItemTitle).filter_by(id=item_id).one()
    return item


def delete_item(item):
    session.delete(item)
    session.commit()


def edit_item(item, name, description, category_id):
    item.name = name
    item.description = description
    item.category_id = category_id
    session.add(item)
    session.commit()
    return item


class ItemTitle(Base):
    __tablename__ = 'item_title'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category.name
        }

if __name__ == '__main__':
    Base.metadata.create_all(engine)
