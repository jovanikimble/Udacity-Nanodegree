-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP TABLE IF EXISTS players;
CREATE TABLE players (
  id serial,
  name text,
  matches integer,
  wins integer
);

DROP TABLE IF EXISTS players;
CREATE TABLE matches (
  id serial,
  pid1 integer,
  pid2 integer,
  winner integer
);
