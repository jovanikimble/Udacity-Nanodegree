# Item Catalog

This program implements an online catalog where you can edit and add items.

## Motivation

The reason this program was created was to implement an understanding of databases and to practice using SQLAlchemy
to create the item catalog database.

## Code Example

Home Page
```
class MainView(MethodView):

    def get(self):
        context = {}
        context['login_session'] = login_session

        categories = session.query(Category).all()

        results = session.query(Category, Item).join(Item).order_by(
            Item.added.desc()).limit(10).all()

        context['categories'] = categories
        context['recent_results'] = results
        return render_template('main.html',context=context)
```
Using third party code

`import psycopg2`
`import flask`
`import SQLAlchemy`

## Installation

Make sure you have **python downloaded and installed.**

If not, download [here](https://www.python.org/downloads/)

Also make sure you have Vagrant installed.

If not, download [here](https://www.vagrantup.com/downloads.html)

Next, clone the following repository:

[HERE](https://github.com/jovanikimble/Udacity-Nanodegree.git)

`cd` to this directory:

$ Udacity-Nanodegree/5project_itemcatalog/project/vagrant

Run these lines in the terminal:

$ vagrant up
$ vagrant ssh

Now you will be inside the Vagrant virtual machine.

First we need to setup the database:

In the terminal run:

$ cd /vagrant/catalog

Then you will use psql to setup the database.

$ psql
$ \i catalog.sql

Now exit out of psql.

To run the itemcatalog code, do the following in the terminal:

$ python webserver.py

One time Set up only:

Navigate to http://localhost:5000/setup

This will respond with a "done" message and the database will be populated.

Now you can Navigate to: http://localhost:5000

