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
--       is_active: A BOOLEAN field that indicates whether an actor is currently active in the film industry (i.e., making films this year).
-- drop existing table and struct having same name in the environment
DROP TABLE actors
DROP TYPE films
DROP TYPE quality_class
-- create films struct to base actors table on it
CREATE TYPE films AS (
filmid TEXT,
film TEXT,
votes INTEGER,
rating REAL
)
-- create enumerated struct for performance quality of actors
CREATE TYPE quality_class AS ENUM ('star','good','average','bad')
-- create table actors structure
CREATE TABLE actors(
yearly_films_index INTEGER,
actorid TEXT,
actor  TEXT,
is_active  BOOLEAN,
movies films[],
quality_class quality_class,
current_year INTEGER,
PRIMARY KEY (yearly_films_index, actorid, current_year) -- an actor can be present in several movies in a year so uniquness comes from this combined PK
);
-- test things
SELECT * FROM actors -- BINGO!
-- 2. Cumulative table generation query: Write a query that populates the actors table one year at a time.

-- lets see when data started in source file: 
SELECT MIN(year) FROM actor_films; -- YAY !! its 1970 we will start populating from 1969 then ! lets go for CTE (Common Tables Expressions) and build temporarily on it till we get result to populate actors' table
SELECT MAX(year) FROM actor_films; 

INSERT INTO actors
WITH RECURSIVE years AS (
   SELECT generate_series(1969, 2021) AS year
   ),
 last_year AS (
   SELECT * FROM actors 
   WHERE current_year = 1969
), 
this_years_data AS(
   SELECT 
   ROW_NUMBER() OVER (PARTITION BY actorid, year ORDER BY film) AS yearly_films_index, *
   FROM actor_films
   WHERE year IN (SELECT year FROM years)
)
SELECT 
      ty.yearly_films_index,
	  COALESCE(ly.actorid, ty.actorid) AS actorid,
	  COALESCE(ly.actor, ty.actor) AS actor,
	  CASE
	     WHEN ty.filmid IS NOT NULL THEN TRUE 
		 ELSE FALSE
	  END AS is_active,
	  CASE 
	    WHEN ly.movies IS NULL THEN ARRAY[ROW(ty.filmid::TEXT, ty.film::TEXT, ty.votes::INTEGER, ty.rating::REAL)::films] 
		WHEN ly.movies IS NOT NULL THEN ly.movies || ARRAY[ROW(ty.filmid::TEXT, ty.film::TEXT, ty.votes::INTEGER, ty.rating::REAL)::films] 
		ELSE ly.movies 
	  END AS movies,
	  CASE 
	   WHEN rating > 8 THEN 'star'
	   WHEN rating <= 8 AND rating > 7 THEN 'good'
	   WHEN rating <= 7 AND rating > 6 THEN 'average'
	   ELSE 'bad'
	  END :: quality_class AS Quality_Class,
	  ty.year AS current_year
FROM last_year ly FULL OUTER JOIN  this_years_data ty
                  ON    ly.actorid = ty.actorid

SELECT * FROM actors
ORDER BY actor, current_year desc