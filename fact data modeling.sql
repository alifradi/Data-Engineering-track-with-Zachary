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

CREATE TABLE user_devices_cumulated (
    user_id NUMERIC NOT NULL,
    device_id NUMERIC NOT NULL,
    browser_type TEXT NOT NULL,
    date DATE NOT NULL, -- Represents the range limit for device activity aggregation
    device_activity_datelist DATE[], -- Aggregated array of active dates
    PRIMARY KEY (user_id, device_id, browser_type, date)
);
-- A cumulative query to generate device_activity_datelist from events
insert into user_devices_cumulated
with yesterday as (
  select * 
  from user_devices_cumulated
  where date = date('2023-01-30') -- Adjust as needed
),
with_users as (
  select user_id, device_id, event_time::date
  from events
),
with_events as (
  select distinct
    us.user_id as user_id,
    us.device_id as device_id,
    us.event_time::date as date,
    d.browser_type as browser_type
  from devices d 
  right join with_users us on us.device_id = d.device_id
  where us.user_id is not null and us.device_id is not null and d.browser_type is not null
  order by date
), 
today as (
  select *
  from with_events 
  where date = date('2023-01-31') -- Adjust as needed
)
select  
  coalesce(t.user_id, y.user_id) as user_id,
  coalesce(t.device_id, y.device_id) as device_id,
  coalesce(t.browser_type, y.browser_type) as browser_type,
  coalesce(t.date, y.date + Interval '1 day')::date as date,
  case 
    when y.device_activity_datelist is not null and t.date is not null then array_append(y.device_activity_datelist, t.date)
    when y.device_activity_datelist is not null then y.device_activity_datelist
    else array[t.date]
  end as device_activity_datelist
from today t
full outer join yesterday y
on 
  y.user_id = t.user_id 
  and y.device_id = t.device_id 
  and y.browser_type = t.browser_type
