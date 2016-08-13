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


name_re = re.compile(r"^[a-zA-Z0-9_-]{1,50}$")
user_re = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
password_re = re.compile(r"^.{3,20}$")
email_re = re.compile(r"^[\S]+@[\S]+.[\S]+$")


def reg_check(text, reg):
    return reg.match(text)


# TODO: delete item page and functionality.
# TODO: json end points
# TODO: oauth login, logout, session state.
# TODO: pages layout and styles.
# Main page. Show game genres and most recently added Titles.
@app.route('/')
@app.route('/category')
def main_page():
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(ItemTitle).order_by(desc(ItemTitle.id)).limit(10)

    return render_template(
        'latest_items.html',
        categories=categories,
        items=items
        )


# Specific category page.  Shows all titles.
@app.route('/category/<int:category_id>/')
def show_category(category_id):
    categories = session.query(Category).order_by(asc(Category.name))
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
    categories = session.query(Category).order_by(asc(Category.name))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']
        field_vals = {}

        user_id = 1  # TODO: replace after implementing user login.

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
    categories = session.query(Category).order_by(asc(Category.name))
    cat = db.get_cat(category_id)
    item = db.get_item(item_id)

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
    cat = db.get_cat(category_id)
    item = db.get_item(item_id)

    return render_template(
        'delete_item.html',
        category=cat,
        item=item
        )

# JSON APIs.


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
