#
# Database access functions for the web forum.
#

import time
import psycopg2
import bleach

## Database connection

## Get posts from database.
def GetAllPosts():
    conn = psycopg2.connect("dbname=forum")

    cursor = conn.cursor()

    cursor.execute("select * from posts order by time desc")

    results = cursor.fetchall()

    conn.close()

    new_results = []

    for r in results:
      d = {}
      d['content'] = r[0]
      d['time'] = str(r[1])
      new_results.append(d)


    return new_results

    posts = [{'content': str(row[1]), 'time': str(row[0])} for row in DB]
    posts.sort(key=lambda row: row['time'], reverse=True)
    return posts

## Add a post to the database.
def AddPost(content):
    conn = psycopg2.connect("dbname=forum")

    cursor = conn.cursor()

    cursor.execute("insert into posts(content) values(%s)",(content,))

    conn.commit()

    conn.close()

    return

    t = time.strftime('%c', time.localtime())
    DB.append((t, content))
