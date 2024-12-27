-- Explore actor_films
SELECT * FROM actor_films ORDER BY rating DESC;

-- 1. DDL (Data Definition Language) for actors table:
-- Drop existing table and struct having the same name in the environment
DROP TABLE IF EXISTS actors;
DROP TYPE IF EXISTS films;
DROP TYPE IF EXISTS quality_class;

-- Create films struct to base actors table on it
CREATE TYPE films AS (
    filmid TEXT,
    film TEXT,
    votes INTEGER,
    rating REAL
);

-- Create enumerated struct for performance quality of actors
CREATE TYPE quality_class AS ENUM ('star', 'good', 'average', 'bad');

-- Create table actors structure
CREATE TABLE actors (
    actorid TEXT,
    actor TEXT,
    active_since INTEGER,
    year INTEGER,
    movies films[],
    is_active BOOLEAN,
    quality_class quality_class,
    PRIMARY KEY (actorid, year) -- An actor can be present in several movies in a year, so cumulate past movies with the current year's movie and PK rows to the current year with actorid
);

-- Test things
SELECT * FROM actors; -- BINGO!

-- 2. Cumulative table generation query:
-- Write a query that populates the actors table one year at a time

-- Let's see when data started in source file:
SELECT MIN(year) FROM actor_films; -- YAY!! It's 1970, we will start populating from 1969 then!
SELECT MAX(year) FROM actor_films;

INSERT INTO actors
WITH years AS (
    SELECT * FROM generate_series(1969, 2021) AS year
), 
actor_startings AS (
    SELECT 
        actorid,
        actor,
        MIN(year) AS active_since 
    FROM actor_films 
    GROUP BY actorid, actor
), actors_seasons AS (
    SELECT *        
    FROM actor_startings
    JOIN years ON years.year >= actor_startings.active_since
    ORDER BY actorid
)
-- END OF CTEs
SELECT DISTINCT 
    ase.actorid, 
    ase.actor, 
    ase.active_since, 
    ase.year,
    array_remove(array_agg(
        CASE WHEN af.actor IS NOT NULL THEN
            ROW(af.filmid, af.film, af.votes, af.rating)::films 
        END
    ) OVER (PARTITION BY ase.actorid ORDER BY COALESCE(ase.year, af.year)), null) AS movies,
    CASE 
        WHEN af.actor IS NULL THEN false ELSE true 
    END AS is_active,
    CASE 
        WHEN AVG(af.rating) OVER (PARTITION BY af.actorid, ase.year) > 8 THEN 'star' 
        WHEN AVG(af.rating) OVER (PARTITION BY af.actorid, ase.year) > 7 THEN 'good' 
        WHEN AVG(af.rating) OVER (PARTITION BY af.actorid, ase.year) > 6 THEN 'average' 
        ELSE 'bad' 
    END::quality_class AS quality_class
FROM actors_seasons ase
LEFT JOIN actor_films af 
    ON af.actorid = ase.actorid 
    AND af.year = ase.year;

-- Select from actors table
SELECT * FROM actors;



--DDL for actors_history_scd table: Create a DDL for an actors_history_scd table with the following features:

-- Implements type 2 dimension modeling (i.e., includes start_date and end_date fields).
-- Tracks quality_class and is_active status for each actor in the actors table.
create table actors_history_scd  (
actorid TEXT,
actor TEXT,
is_active boolean,
quality_class quality_class,
start_date integer,
end_date integer
);



WITH with_previous AS (
  SELECT 
      actorid,
      actor,
      year AS production_year,
      quality_class,
	  is_active,
      LAG(quality_class, 1) OVER (PARTITION BY actor, actorid ORDER BY year) AS previous_class,
      LAG(is_active, 1) OVER (PARTITION BY actor, actorid ORDER BY year) AS previous_is_active
  FROM actors
), with_indicators AS (
  SELECT 
      *,
      CASE 
          WHEN previous_class <> quality_class OR is_active <> previous_is_active 
          THEN 1
          ELSE 0
      END AS changed
  FROM with_previous
), with_streaks AS (
  SELECT 
      *,
      SUM(changed) OVER (PARTITION BY actorid, actor ORDER BY production_year) AS streak_identifier
  FROM with_indicators
)
SELECT
  actorid,
  actor,
  streak_identifier,
  is_active,
  quality_class,
  MIN(production_year) AS start_date,
  MAX(production_year) AS end_date
FROM with_streaks
GROUP BY actorid, actor, is_active, quality_class, streak_identifier
order by actor, start_date

