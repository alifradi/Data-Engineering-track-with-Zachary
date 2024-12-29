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

with missings as(
select count(*) as all_rows, count(user_id) as non_missing_users
from events)
select all_rows-non_missing_users as null_usersid
from missings -- 3048 out of 13782 are null

select * from events where user_id is null

select * from devices
-- print column names from devices
SELECT column_name 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE table_name = 'devices'; -- device_id,browser_version_patch,device_version_minor,device_version_patch,os_version_minor,os_version_patch,browser_version_major,browser_version_minor,browser_type,device_version_major,os_type,os_version_major, device_type

-- A DDL for an user_devices_cumulated table that has:

--   a device_activity_datelist which tracks a users active days by browser_type
--   data type here should look similar to MAP<STRING, ARRAY[DATE]>
--   or you could have browser_type as a column with multiple rows for each user (either way works, just be consistent!)

-- browser_type from device
-- device_id, user_id from events

-- Option 1: This approach uses a map where the key is the browser_type and the value is an array of dates representing the active days. This structure is compact and efficient for querying a user's activity by browser type.
-- Option 2: This approach uses multiple rows for each user, with each row representing an active day for a specific browser_type. This structure is more normalized and can be easier to work with in some SQL databases that do not support complex data types like maps and arrays.

with with_users as (
 select user_id, device_id, event_time
 from events
)
select 
us.user_id,
us.device_id,
us.event_time,
d.browser_version_patch,
d.device_version_minor,
d.device_version_patch,
d.os_version_minor,
d.os_version_patch,
d.browser_version_major,
browser_version_minor,
d.browser_type,
d.device_version_major,
d.os_type,
d.os_version_major,
d.device_type
from devices d 
left join with_users us on us.device_id=d.device_id


with with_users as (
 select user_id, device_id, event_time
 from events
),
with_events as (
select 
us.user_id,
us.device_id,
us.event_time,
d.browser_type
from devices d 
left join with_users us on us.device_id=d.device_id
)
select 
  map
