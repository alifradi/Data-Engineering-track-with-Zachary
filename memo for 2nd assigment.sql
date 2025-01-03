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
