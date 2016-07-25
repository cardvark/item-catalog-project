from sqlalchemy.orm import sessionmaker
from database_setup_catalog import Base, User, Category, ItemTitle, engine


Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# User functions
def create_user(name, email, picture):
    new_user = User(
        name=name,
        email=email,
        picture=picture
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


# def del_user(user_id):
#     user = session.query(User).filter_by(id=user_id).one()
#     session.delete(user)
#     session.commit()


# Category functions
def create_category(name):
    new_category = Category(name=name)
    session.add(new_category)
    session.commit()
    return new_category.id


def get_items_in_category(category_name):
    pass


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
    return new_item.id
