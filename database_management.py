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

    game_tuples = [
        (
            'Lego Star Wars: The Force Awakens',
            'It\'s a Star Wars game, but lego.  Pretty cool, man.  All the lego, all the star wars.  And full of funny shit.  Good times.',
            'Action'
            ),
        (
            'Mirror\'s Edge Catalyst',
            'The long awaited (maybe?) sequel to the original Mirror\'s Edge. You run and jump and parkour and stuff.  It\'s probably pretty bad for motion sickness.',
            'Action'
            ),
        (
            'The Walking Dead',
            'Breakout hit series from Telltale Games.  Cartoonish and comicky, but only in art style.  Totally dark and fucked up. You\'re gonna make some rough decisions along the way.',
            'Adventure'
            ),
        (
            'The Wolf Among Us',
            'Another Telltale game, based on some kind of grimm\'s fairy tales comic. It\'s pretty awesome. Very dark. Hoping to see more of this in the future.',
            'Adventure'
            ),
        (
            'Dead or Alive',
            'Decent fighting game. Best known for its extremely buxom fighters. Has a spinoff beach volleyball game. They knew exactly what they were doing.',
            'Fighting'
            ),
        (
            'Street Fighter V',
            'The fifth (hahaha) entry in the Street Fighter series. Okay, no idea how many entries there have been. A whole frickin lot, that\'s how many.',
            'Fighting'
            ),
        (
            'Super Mario Bros.',
            'The original NES game. It\'s really old.',
            'Platformer'
            ),
        (
            'Super Meat Boy',
            'You\'re a red brick of meat, and you\'re trying to save your girlfriend brick of meat, I think. Never actually played this, but it had great reviews.',
            'Platformer'
            ),
        (
            'Final Fantasy XIII',
            'Came out for the PS3, so it\'s actually pretty old. People complained about how on-rails the early experience was. Also got a bad rap for how straight forward the combat was, early on. I liked the paradigm system though - lots of active switching was fun.',
            'RPG'
            ),
        (
            'The Walking Dead: Road to Survival',
            'It\'s an RPG with city builder elements. Pretty significant city builder elements. Brunt of focus is around the characters and combat.',
            'RPG'
            ),
        (
            'Call of Duty',
            'When duty calls, be quick to answer. Shoot stuff, kill folks, all that jazz.',
            'Shooter'
            ),
        (
            'Overwatch',
            'Blizzard\'s big attempt to take on Team Fortress 2. Fairly successful so far. Good ideas. Was fun for the two matches I bothered to play.',
            'Shooter'
            ),
        (
            'Madden NFL',
            'It\'s a game about being really mad while playing football. Or mad while inside of a foot ball. "Mad in football," so to speak.',
            'Sports'
            ),
        (
            'Rocket League',
            'Apparently it\'s soccer, but with cars. Sounds weird. A lot of people like it, though. It\'s one of those games I figure I might like if I actually tried it out, but I don\'t really care.',
            'Sports'
            ),
        (
            'Clash of Clans',
            'It\'s a strategy game, sort of. On mobile. Whatever.',
            'Strategy'
            ),
        (
            'Starcraft',
            'Pretty serious series for real time strategy games. Hella popular in Korea. I enjoyed the single player campaign of Starcraft II, but never bothered w/ the multiplayer or the follow up episodes.',
            'Strategy'
            )
    ]

    for tup in game_tuples:
        create_item(
            tup[0],
            tup[1],
            get_cat_id(tup[2]),
            1
            )


if __name__ == '__main__':
    add_users()
    fill_categories()
    fill_items()
