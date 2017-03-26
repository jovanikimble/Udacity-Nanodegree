# Tournament Results

This program is an implentation of a Swiss System Tournament run from the command line. The program maintains a database of players and records their matches, and wins. Also, per match winners and losers are recorded in the database.

## Motivation

The reason this program was created was to implement an understanding of databases and to practice writing SQl not vulnerable to SQL injection. This program is not advanced, however includes important fundamentals of database creation and management.

## Code Example

Counts Players
```
def countPlayers():
    """Returns the number of players registered."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('select count (*) from players;')
    results = cursor.fetchall()
    conn.close()

    return int(results[0][0])
```
Using third party code

`import psycopg2`

## Installation

Make sure you have **python downloaded and installed.**

If not, download [here](https://www.python.org/downloads/)

Also make sure you have Vagrant installed.

If not, download [here](https://www.vagrantup.com/downloads.html)

Next, clone the following repository:

[HERE](https://github.com/jovanikimble/Udacity-Nanodegree.git)

`cd` to this directory:

$ Udacity-Nanodegree/4project_tournamentresults/project

Run these lines in the terminal:

$ vagrant up
$ vagrant ssh

Now you will be inside the Vagrant virtual machine.

First we need to setup the database:

In the terminal run:

$ cd /vagrant/tournament

Then you will use psql to setup the database.

$ psql
$ \i tournament.sql

Now exit out of psql (Ctrl + D).

To run the tournament code, do the following in the terminal:

$ python tournament_test.py
