-- The homework this week will be using the devices and events dataset

-- Construct the following eight queries:

--    1. A query to deduplicate game_details from Day 1 so there's no duplicates

SELECT * FROM game_details -- 492068 rows

SELECT *
FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY game_id, team_id) AS row_num
    FROM game_details
) AS games_deduped
WHERE row_num = 1; -- 18768 rows 96% less data
