select 
min(event_time),
max(event_time)
from events

select * from events

drop table users_cumulated
create table users_cumulated (
user_id text,
dates_active date[],
date date,
primary key(user_id,date)
)

INSERT INTO users_cumulated
WITH date_range AS (
    -- Generate all dates in January 2023
    SELECT generate_series(
        '2023-01-01'::DATE,
        '2023-01-31'::DATE,
        '1 day'::INTERVAL
    )::DATE AS date
),
all_events AS (
    -- Get all events with their active dates
    SELECT 
        user_id::TEXT AS user_id,
        DATE(CAST(event_time AS TIMESTAMP)) AS date_active
    FROM events
    WHERE DATE(CAST(event_time AS TIMESTAMP)) BETWEEN '2023-01-01' AND '2023-01-31'
      AND user_id IS NOT NULL
    GROUP BY user_id, DATE(CAST(event_time AS TIMESTAMP))
),
cumulative_dates AS (
    -- Accumulate active dates for each user up to each date
    SELECT
        d.date,
        e.user_id,
        ARRAY_AGG(e.date_active) FILTER (WHERE e.date_active <= d.date) AS dates_active
    FROM date_range d
    LEFT JOIN all_events e
        ON e.date_active <= d.date
    GROUP BY d.date, e.user_id
),
final_result AS (
    -- Ensure consistent user records by combining with existing data
    SELECT
        COALESCE(c.user_id, u.user_id) AS user_id,
        ARRAY_CAT(
            COALESCE(u.dates_active, ARRAY[]::DATE[]),
            COALESCE(c.dates_active, ARRAY[]::DATE[])
        ) AS dates_active,
        c.date
    FROM cumulative_dates c
    FULL OUTER JOIN users_cumulated u
        ON c.user_id = u.user_id AND c.date = u.date
)
SELECT * FROM final_result;


select * from users_cumulated
order by user_id, date




WITH users AS (
    SELECT * 
    FROM users_cumulated 
    WHERE date = DATE('2023-01-31')
),
series AS (
    SELECT 
        generate_series(DATE('2023-01-01'), DATE('2023-01-31'), INTERVAL '1 day')::DATE AS series_date
), place_holder_in as(
SELECT 
    user_id,
    date,
    dates_active,
    CASE 
        WHEN dates_active @> ARRAY[series.series_date] THEN 
            POWER(2, date - series.series_date)::BIGINT
        ELSE 
            0
    END AS place_holder_int -- Casting to bit(32) here
FROM users
CROSS JOIN series
)
select user_id,
sum(place_holder_int)::bigint::bit(32) as history_active,
bit_count(sum(place_holder_int)::bigint::bit(32)) as days_active,
bit_count('10000000000000000000000000000000'::bit(32)& sum(place_holder_int)::bigint::bit(32) )>0 as weekly_active,
bit_count('11111110000000000000000000000000'::bit(32)& sum(place_holder_int)::bigint::bit(32) )>0 as weekly_active,
bit_count(sum(place_holder_int)::bigint::bit(32) )>0 as dayly_active
from place_holder_in
group by user_id

