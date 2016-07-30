from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from flask import session as login_session
import random
import string
app = Flask(__name__)

from sqlalchemy import asc, desc
from sqlalchemy.orm import sessionmaker

from database_setup_catalog import Base, User, Category, ItemTitle, engine
import database_setup_catalog as db

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# TODO: html templates.  Base page, individual pages.
# TODO: pages functionality
# TODO: pages layout and styles.
# Main page. Show game genres and most recently added Titles.
@app.route('/')
@app.route('/category')
def main_page():
    categories = session.query(Category).all()
    items = session.query(ItemTitle).order_by(desc(ItemTitle.id)).limit(10)

    return render_template('main.html', categories=categories, items=items)


# Specific category page.  Shows all titles.
@app.route('/category/<int:category_id>/')
def show_category(category_id):
    cat = db.get_cat(category_id)
    return 'Individual category page.  {category}'.format(category=cat.name)


# Item page. Shows desc.
@app.route('/category/<int:category_id>/<int:item_id>/')
def show_item(category_id, item_id):
    cat = db.get_cat(category_id)
    item = db.get_item(item_id)
    return 'Specific item page.  Category: {category}, Item: {item}'.format(
        category=cat.name,
        item=item.name
        )


# Add item page.
@app.route(
    '/category/<int:category_id>/new/',
    methods=['GET', 'POST']
    )
def add_item(category_id):
    cat = db.get_cat(category_id)
    return 'Add new item to {category}'.format(category=cat.name)


# Edit item page.
@app.route(
    '/category/<int:category_id>/<int:item_id>/edit/',
    methods=['GET', 'POST']
    )
def edit_item(category_id, item_id):
    cat = db.get_cat(category_id)
    item = db.get_item(item_id)
    return 'Edit item page.  Category: {category}, Item: {item}'.format(
        category=cat.name,
        item=item.name
        )


# JSON APIs.


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
