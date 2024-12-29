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

-- Exploring data
select * from events -- url,referrer, user_id, device_id, host, event_time
select distinct host from events -- 3 values
select distinct device_id from events -- 349
select distinct event_time from events --8415
select distinct user_id from events -- 1432
select distinct url from events -- 382
select distinct referrer from events -- 163

select * from devices
-- print column names from devices
SELECT column_name 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE table_name = 'devices'; -- device_id,browser_version_patch,device_version_minor,device_version_patch,os_version_minor,os_version_patch,browser_version_major,browser_version_minor,browser_type,device_version_major,os_type,os_version_major, device_type
