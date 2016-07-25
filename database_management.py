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


def get_cat_id(name):
    cat = session.query(Category).filter_by(name=name).one()
    return cat.id


def get_items_in_category(category_name):
    items_list = session.query(ItemTitle).join(ItemTitle.category).filter_by(name=category_name)
    return items_list


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


# set up functions:

def add_users():
    user_list = [
        ['Bob Michaels', 'bob.michael@email.com', 'http://picture_url.com']
    ]

    for user in user_list:
        create_user(user[0], user[1], user[2])


def fill_categories():
    cat_list = [
        'Action',
        'Adventure',
        'Fighting',
        'Platformer',
        'RPG',
        'Shooter',
        'Strategy',
        'Sports'
    ]

    for cat in cat_list:
        create_category(cat)


def fill_items():
    def action_cat():
        cat_id = get_cat_id('Action')

        create_item(
            'Lego Star Wars: The Force Awakens',
            'It\'s a Star Wars game, but lego.  Pretty cool, man.  All the lego, all the star wars.  And full of funny shit.  Good times.',
            cat_id,
            1
            )
        create_item(
            'Mirror\'s Edge Catalyst',
            'The long awaited (maybe?) sequel to the original Mirror\'s Edge. You run and jump and parkour and stuff.  It\'s probably pretty bad for motion sickness.',
            cat_id,
            1
            )

    def adventure_cat():
        cat_id = get_cat_id('Adventure')

        create_item(
            'The Walking Dead',
            'Breakout hit series from Telltale Games.  Cartoonish and comicky, but only in art style.  Totally dark and fucked up. You\'re gonna make some rough decisions along the way.',
            cat_id,
            1
            )

    action_cat()
    adventure_cat()
