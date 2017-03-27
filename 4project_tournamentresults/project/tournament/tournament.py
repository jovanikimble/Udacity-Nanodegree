#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import sys

def connect(dbname="tournament"):
    """Connect to the PostgreSQL database.  Returns a database connection."""
    try:
        conn = psycopg2.connect("dbname={0}".format(dbname))
        cursor = conn.cursor()
        return conn, cursor
    except:
        print("Connection could not be made")
        sys.exit(1)

def deleteMatches():
    """Remove all the match records from the database."""
    conn, cursor = connect()
    cursor.execute('TRUNCATE matches;')
    conn.commit()
    conn.close()


def deletePlayers():
    """Remove all the player records from the database."""
    conn, cursor = connect()
    cursor.execute('TRUNCATE players CASCADE;')
    conn.commit()
    conn.close()


def countPlayers():
    """Returns the number of players currently registered."""
    conn, cursor = connect()
    cursor.execute('select count (*) from players;')
    result = cursor.fetchone()
    conn.close()

    return int(result[0])


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    conn, cursor = connect()
    cursor.execute('insert into players(name) values(%s);', (name,))
    conn.commit()
    conn.close()

def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn, cursor = connect()
    cursor.execute(
        'CREATE TEMP VIEW loss1 AS SELECT loser, COUNT(loser) as losses FROM matches GROUP BY loser;'
        'CREATE TEMP VIEW wins1 AS SELECT winner, COUNT(winner) as wins FROM matches GROUP BY winner;'
        'CREATE TEMP VIEW t1 AS SELECT COALESCE(loser, winner) as id, COALESCE(losses, 0) as losses, COALESCE(wins, 0) as wins FROM loss1 FULL OUTER JOIN wins1 ON loser = winner;'
        'SELECT players.id, players.name, COALESCE(t1.wins, 0), COALESCE(t1.wins + t1.losses, 0) FROM players LEFT JOIN t1 ON t1.id = players.id ORDER BY wins DESC;'
    )
    results = cursor.fetchall()
    conn.close()

    return results


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """

    conn, cursor = connect()
    cursor.execute('insert into matches(winner, loser) values(%s, %s)', (winner,loser))
    conn.commit()
    conn.close()



def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """

    results = playerStandings()

    pairs = []

    count = 0

    # Players have already been sorted. This matches
    # similar players based on their wins for a match.
    for i in xrange(len(results)/2):
        tup = (results[count][0],results[count][1],
               results[count+1][0],results[count+1][1])

        pairs.append(tup)
        count += 2

    return pairs