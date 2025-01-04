with deduped as (
select 
g.game_date_est,
gd.*, 
row_number() over (partition by player_id, gd.game_id, team_id order by g.game_date_est) as row_num 
from game_details gd
join games g on gd.game_id = g.game_id
)
select * 
from deduped 
where row_num =1 


select* from game_details



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
bit_count('10000000000000000000000000000000'::bit(32)& sum(place_holder_int)::bigint::bit(32) )>0 as last_day_active,
bit_count('11111110000000000000000000000000'::bit(32)& sum(place_holder_int)::bigint::bit(32) )>0 as last_week_active,
bit_count(sum(place_holder_int)::bigint::bit(32) )>0 as daily_active
from place_holder_in
group by user_id




create table array_metrics (
user_id numeric,
month_start date,
metric_name text,
metric_array real[]
,primary key (user_id, month_start, metric_name)
)

delete from array_metrics
-- Insert aggregated metrics into the array_metrics table
INSERT INTO array_metrics
WITH daily_aggregate AS (
    -- Aggregate daily site hits per user
    SELECT 
        user_id,
        DATE(event_time) AS date,
        COUNT(1) AS num_site_hits
    FROM events
    WHERE DATE(event_time) = DATE('2023-01-03')
    AND user_id IS NOT NULL
    GROUP BY user_id, DATE(event_time)
),
yesterday_array AS (
    -- Retrieve existing metrics for the month starting from '2023-01-01'
    SELECT *
    FROM array_metrics 
    WHERE month_start = DATE('2023-01-01')
)
SELECT 
    -- Select user_id from either daily_aggregate or yesterday_array
    COALESCE( da.user_id, ya.user_id) AS user_id,
    -- Determine month_start date
    COALESCE(ya.month_start, DATE_TRUNC('month', da.date)) AS month_start,
    -- Set metric name to 'site_hits'
    'site_hits' AS metric_name,
    -- Update metric_array based on existing data and new daily aggregates
    CASE 
        WHEN ya.metric_array IS NOT NULL THEN 
            ya.metric_array || ARRAY[COALESCE(da.num_site_hits,0)] 
        WHEN ya.metric_array IS NULL THEN
            ARRAY_FILL(0, ARRAY[COALESCE (date - DATE(DATE_TRUNC('month', date)), 0)]) 
                || ARRAY[COALESCE(da.num_site_hits,0)]
    END AS metric_array
FROM daily_aggregate da
FULL OUTER JOIN yesterday_array ya 
ON da.user_id = ya.user_id
ON CONFLICT (user_id, month_start, metric_name)
DO 
    UPDATE SET metric_array = EXCLUDED.metric_array;


select * from array_metrics

-- Uncomment and run the following query to verify the cardinality of metric_array
-- SELECT cardinality(metric_array), COUNT(1)
-- FROM array_metrics
-- GROUP BY 1;

-- Aggregate metrics by summing specific elements in the metric_array
WITH agg AS (
    SELECT metric_name, month_start, ARRAY[SUM(metric_array[1]), SUM(metric_array[2]), SUM(metric_array[3])] AS summed_array
    FROM array_metrics
    GROUP BY metric_name, month_start
)
-- Select and display the metric_name, date (adjusted by index), and summed value
SELECT 
    metric_name, 
    month_start + CAST(CAST(index - 1 AS TEXT) || ' day' AS INTERVAL) AS adjusted_date,
    elem AS value
FROM agg
CROSS JOIN UNNEST(agg.summed_array) WITH ORDINALITY AS a(elem, index);
