# Grader setup

Here is how you SSH into the machine:

ssh grader@34.203.220.55 -p 2200 -i ~/.ssh/udacity_rsa

Passphrase: blueberrykoolaid

(The RSA key is provided in the project folder)

You can view the website by going to:

http://34.203.220.55

# Linux Server

This project shows how you can host an online catalog on a linux server.

## Motivation

The reason this project was created was to get experience setting up and hosting applications on a remote server.


Using third party applications

This project configuration depends on using Amazon Lightsail.

## Demo
  Live Version at: http://34.203.220.55/

## Installation

Make sure you sign up for Amazon Lighsail.

Now, assuming you have Amazon Lightsail setup and are SSH'd into the machine, run these instructions:

Updating libraries

$ sudo apt-get update

Installing Apache

$ sudo apt-get install apache2

Upgrading install libraries

$ sudo apt-get upgrade

Install pip

$ sudo apt-get install python-pip

pg_config.sh

sudo apt-get -qqy update
sudo apt-get -qqy install postgresql python-psycopg2
sudo apt-get -qqy install python-flask python-sqlalchemy
sudo apt-get -qqy install python-pip
pip install bleach
pip install oauth2client
pip install requests
pip install httplib2
pip install redis
pip install passlib
pip install itsdangerous
pip install flask-httpauth

Set up the postgres user

$ sudo -u postgres -i
$ createuser -dRS ubuntu
$ createdb ubuntu

Setting up the grader user
$ sudo adduser grader
(pw grader123)
Full name: Grader
Room: 123

$ sudo vi /etc/sudoers.d/grader
grader ALL=(ALL) NOPASSWD:ALL

Generate a keypair
$ ssh-keygen
(Passphrase used was blueberrykoolaid)

Back on the remote machine
$ mkdir .ssh
$ vi .ssh/authorized_keys
(Copied publickey from /Users/jovanikimble/.ssh/udacity_rsa.pub)
$ chmod 700 .ssh
$ chmod 644 .ssh/authorized_keys

Now what works is:
ssh grader@34.203.220.55 -p 22 -i ~/.ssh/udacity_rsa
(Use passphrase: blueberrykoolaid)

Now back to the remote machine
$ sudo vi /etc/ssh/sshd_config
(Change to PasswordAuthentication no)

$ sudo service ssh restart

(Looking at ssh documentation for Lightsail here)

$ sudo vi /etc/ssh/sshd_config
  Port 2200

$ sudo service ssh restart

ssh grader@34.203.220.55 -p 2200 -i ~/.ssh/udacity_rsa

Now the files are copied from my source code to the remote location

(Logged in as user grader)

cd project/vagrant/catalog

$  sudo -u postgres -i

$ createuser -dRS grader

$ createdb grader

Change ALTER USER 'vagrant' to ALTER USER 'grader'

$ psql

$ \i catalog.sql

Command + D to exit.

Also in database_setup.py the SQLAlchemy URL needs to be changed to the grader user.

$ pip install httplib2

$ sudo apt-get install libapache2-mod-wsgi

$ vi /etc/apache2/sites-enabled/000-default.conf

Added
WSGIDaemonProcess myapp user=grader
WSGIScriptAlias / /var/www/html/myapp.wsgi
  <Directory /var/www/html>
    WSGIProcessGroup myapp
    WSGIApplicationGroup %{GLOBAL}
    Order deny,allow
    Allow from all
  </Directory>

$ sudo apache2ctl restart

$ export PYTHONPATH="${PYTHONPATH}:/home/grader/project/project/vagrant/catalog"

$ sudo vi /var/www/html/myapp.wsgi

import sys
sys.path.append('/home/grader/project/project/vagrant/catalog')
sys.path.append('/usr/lib/python2.7/dist-packages')
sys.path.append('/home/grader/.local/lib/python2.7/site-packages')

sys.stdout = sys.stderr

from webserver import app as application

$ sudo apache2ctl restart


