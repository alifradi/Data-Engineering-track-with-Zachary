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
