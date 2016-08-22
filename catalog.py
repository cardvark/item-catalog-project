from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from flask import session as login_session
import random
import string
import re
app = Flask(__name__)

from sqlalchemy import asc, desc
from sqlalchemy.orm import sessionmaker

from database_setup_catalog import Base, User, Category, ItemTitle, engine
import database_setup_catalog as db

import time

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# client id:
# 870763511066-vro9k71bo250ertvcumeokil0gfv8a0m.apps.googleusercontent.com

# client secret:
# hBO3aKQCdR3DWrRN-auVY388
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = 'Item Catalog'

name_re = re.compile(r"^[a-zA-Z0-9_-]{1,50}$")
user_re = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
password_re = re.compile(r"^.{3,20}$")
email_re = re.compile(r"^[\S]+@[\S]+.[\S]+$")


def reg_check(text, reg):
    return reg.match(text)


# TODO: oauth login, logout, session state.
# TODO: pages layout and styles.


# Main page. Show game genres and most recently added Titles.
@app.route('/')
@app.route('/category')
def main_page():
    categories = db.get_all_categories()
    items = session.query(ItemTitle).order_by(desc(ItemTitle.id)).limit(10)

    return render_template(
        'latest_items.html',
        categories=categories,
        items=items
        )


# Specific category page.  Shows all titles.
@app.route('/category/<int:category_id>/')
def show_category(category_id):
    categories = db.get_all_categories()
    cat = db.get_cat(category_id)
    items = session.query(ItemTitle).filter_by(category_id=cat.id).order_by(asc(ItemTitle.name))
    return render_template(
        'category.html',
        categories=categories,
        category=cat,
        items=items
        )


# Item page. Shows desc.
@app.route('/category/<int:category_id>/<int:item_id>/')
def show_item(category_id, item_id):
    cat = db.get_cat(category_id)
    item = db.get_item(item_id)
    return render_template(
        'item.html',
        category=cat,
        item=item
        )


# Add item page.
@app.route(
    '/category/new/',
    defaults={'category_id': None},
    methods=['GET', 'POST']
    )
@app.route(
    '/category/new/<int:category_id>/',
    methods=['GET', 'POST']
    )
def new_item(category_id):
    if 'username' not in login_session:
        return redirect(url_for('show_login'))

    categories = db.get_all_categories()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']
        field_vals = {}

        user_id = login_session['user_id']

        if name and description and category != "None":
            print 'received inputs'
            flash('New item added!')
            cat_id = db.get_cat_id(category)
            new_item = db.create_item(
                name,
                description,
                cat_id,
                user_id
                )
            return redirect(url_for(
                'show_item',
                category_id=cat_id,
                item_id=new_item.id
                )
            )
        elif category == "None":
            flash('Must enter a category.')
        else:
            field_vals['default_cat'] = category
            flash('Invalid input! Must enter values.')

        field_vals['input_name'] = name
        field_vals['input_description'] = description
        return render_template('new_item.html', categories=categories, **field_vals)
    else:
        if category_id:
            cat_name = db.get_cat(category_id).name
            return render_template('new_item.html', categories=categories, default_cat=cat_name)
        else:
            return render_template('new_item.html', categories=categories)


# Edit item page.
@app.route(
    '/category/<int:category_id>/<int:item_id>/edit/',
    methods=['GET', 'POST']
    )
def edit_item(category_id, item_id):
    if 'username' not in login_session:
        return redirect(url_for('show_login'))

    categories = db.get_all_categories()
    cat = db.get_cat(category_id)
    item = db.get_item(item_id)
    user_id = login_session['user_id']

    if item.user_id != user_id:
        return redirect(url_for('main_page'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']
        # user_id = 1  # TODO: replace after implementing user login.

        field_vals = {}

        if name and description:
            flash('Item edited!')
            db.edit_item(item, name, description, db.get_cat_id(category))

            time.sleep(1)
            return redirect(url_for(
                'show_item',
                category_id=category_id,
                item_id=item_id
                )
            )
        else:
            field_vals['default_cat'] = category
            flash('Invalid input! Must enter values.')

        field_vals['input_name'] = name
        field_vals['input_description'] = description
        return render_template('new_item.html', categories=categories, **field_vals)
    else:
        return render_template(
            'edit_item.html',
            category_id=category_id,
            item_id=item_id,
            categories=categories,
            input_name=item.name,
            input_description=item.description,
            default_cat=cat.name
            )


@app.route(
    '/category/<int:category_id>/<int:item_id>/delete/',
    methods=['GET', 'POST']
    )
def delete_item(category_id, item_id):
    if 'username' not in login_session:
        return redirect(url_for('show_login'))

    cat = db.get_cat(category_id)
    item = db.get_item(item_id)

    user_id = login_session['user_id']

    if item.user_id != user_id:
        return redirect(url_for('main_page'))

    if request.method == 'POST':
        delete_confirmation = request.form['delete']

        if delete_confirmation == 'yes':
            db.delete_item(item)
            flash('Item entry deleted.')
        return redirect(url_for('show_category', category_id=cat.id))
    else:
        return render_template(
            'delete_item.html',
            category=cat,
            item=item
            )


# login handling
@app.route('/login')
def show_login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = request.data
    print 'Access token received {token}'.format(token=access_token)

    fb_client_json = open('fb_client_secrets.json', 'r').read()

    app_id = json.loads(fb_client_json)['web']['app_id']
    app_secret = json.loads(fb_client_json)['web']['app_secret']
    token_url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id={id}&client_secret={secret}&fb_exchange_token={token}'.format(
        id=app_id,
        secret=app_secret,
        token=access_token
        )
    h = httplib2.Http()
    result = h.request(token_url, 'GET')[1]

    base_url = 'https://graph.facebook.com/v2.4/me'

    token = result.split('&')[0]

    userinfo_url = base_url + '?{token}&fields=name,id,email'.format(token=token)
    h = httplib2.Http()
    user_result = h.request(userinfo_url, 'GET')[1]

    user_data = json.loads(user_result)
    login_session['provider'] = 'facebook'
    login_session['username'] = user_data['name']
    login_session['email'] = user_data['email']
    login_session['facebook_id'] = user_data['id']

    stored_token = token.split('=')[1]
    login_session['access_token'] = stored_token

    pic_url = base_url + '/picture?{token}&redirect=0&height=200&width=200'.format(token=token)
    h = httplib2.Http()
    pic_result = h.request(pic_url, 'GET')[1]
    pic_data = json.loads(pic_result)

    login_session['picture'] = pic_data['data']['url']

    user_id = db.get_user_id(login_session['email'])

    if not user_id:
        user_id = db.create_user(login_session)

    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash('Now logged in as {name}'.format(name=login_session['username']))
    return output


@app.route('/fbdisconnect', methods=['POST'])
def fbdisconnect():
    facebook_id = login_session['facebook_id']

    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/{id}/permissions?access_token={token}'.format(
        id=facebook_id,
        token=access_token
        )
    h = httplib2.Http()
    result = json.loads(h.request(url, 'DELETE')[1])

    if not result.get('success'):
        response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response

    return 'You have been logged out'


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    code = request.data

    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = credentials.access_token

    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={token}'.format(token=access_token))
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    gplus_id = credentials.id_token['sub']

    if result['user_id'] != gplus_id:
        response = make_response(json.dumps('Token\'s user ID doesn\'t match given user ID.'), 401)
        response.heads['Content-Type'] = 'application/json'
        return response

    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps('Token\'s client ID does not match app\'s.'), 401)
        print 'Token\'s client ID does not match app\'s.'
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {
        'access_token': credentials.access_token,
        'alt': 'json'
        }
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    user_id = db.get_user_id(login_session['email'])

    if user_id is None:
        user_id = db.create_user(login_session)

    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash('You are now logged in as {name}'.format(name=login_session['username']))
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    print 'In gdisconnect, access token is {token}'.format(token=access_token)
    print 'User name is: '
    print login_session.get('username')

    if access_token is None:
        print 'Access token is None'
        response = make_response(json.dumps('Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token={token}'.format(token=access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] != '200':
        response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# Universal
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['user_id']
        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['provider']

        flash('You have been successfully logged out.')
    else:
        flash('You were not logged in.')

    return redirect(url_for('main_page'))


# JSON APIs.
@app.route('/category/JSON')
def categories_json():
    categories = session.query(Category).all()
    return jsonify(Categories=[cat.serialize for cat in categories])


@app.route('/category/<int:category_id>/JSON')
def category_items_json(category_id):
    item_list = db.get_items_in_category(category_id)
    category = db.get_cat(category_id)
    return jsonify(Category=category.name, Items=[item.serialize for item in item_list])
    # return jsonify(Items=[item.serialize for item in item_list])


@app.route('/category/<int:category_id>/<int:item_id>/JSON')
def item_json(category_id, item_id):
    item = db.get_item(item_id)
    return jsonify(Item=item.serialize)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
