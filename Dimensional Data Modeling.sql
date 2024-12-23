-- explore actor_films
select * from actor_films

-- 1. DDL (Data Definition Language) for actors table: Create a DDL for an actors table with the following fields:
--       films: An array of struct with the following fields:
--              film: The name of the film.
--              votes: The number of votes the film received.
--              rating: The rating of the film.
--              filmid: A unique identifier for each film.
--       quality_class: This field represents an actor's performance quality, determined by the average rating of movies of their most recent year. It's categorized as follows:
--              star: Average rating > 8.
--              good: Average rating > 7 and ≤ 8.
--              average: Average rating > 6 and ≤ 7.
--              bad: Average rating ≤ 6.
-- drop existing table and struct having same name in the environment
DROP TABLE actors
DROP TYPE films
DROP TYPE quality_class
-- create films struct to base actors table on it
CREATE TYPE films AS (
film TEXT,
votes INTEGER,
rating REAL,
filmid TEXT
)
--
CREATE TYPE quality_class AS ENUM ('star','good','average','bad')