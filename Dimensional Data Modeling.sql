-- explore actor_films
select * from actor_films order by rating desc

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
actorid TEXT,
actor  TEXT,
active_since INTEGER,
year INTEGER,
movies films[],
is_active  BOOLEAN,
quality_class quality_class,
PRIMARY KEY (actorid, year) -- an actor can be present in several movies in a year so cumulate past movies with current year's movie and PK rows to current year with actorid
);
-- test things
SELECT * FROM actors -- BINGO!
-- 2. Cumulative table generation query: Write a query that populates the actors table one year at a time.

-- lets see when data started in source file: 
SELECT MIN(year) FROM actor_films; -- YAY !! its 1970 we will start populating from 1969 then ! lets go for CTE (Common Tables Expressions) and build temporarily on it till we get result to populate actors' table
SELECT MAX(year) FROM actor_films; 

insert into actors
with years as (
  select * from generate_series(1969,2021) AS year
), 
actor_startings as (
  select 
        actorid,
		actor,
		min(year) as active_since 
  from actor_films 
  group by actorid, actor
), actors_seasons as(
select *        
from actor_startings
join years  on years.year >= actor_startings.active_since
order by actorid)
--END OF CTEs
select distinct ase.actorid, ase.actor, ase.active_since, ase.year,
       array_remove(array_agg(case when af.actor is not null then
	                               row(af.filmid, af.film,af.votes,af.rating)::films end)
								   over (partition by ase.actorid order by coalesce(ase.year,af.year)), 
							   null
	                ) as movies,
	   case when af.actor is null then false else true end as is_active,
	    CASE 
	        WHEN avg(af.rating) OVER (PARTITION BY af.actorid, ase.year) > 8 THEN 'star' 
	        WHEN avg(af.rating) OVER (PARTITION BY af.actorid, ase.year) > 7 THEN 'good' 
			WHEN avg(af.rating) OVER (PARTITION BY af.actorid, ase.year) > 6 THEN 'average' 
			ELSE 'bad' END::quality_class AS Quality_Class
from actors_seasons ase
left join actor_films af on
                         af.actorid = ase.actorid and af.year = ase.year					


select * from actors
