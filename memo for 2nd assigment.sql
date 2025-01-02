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
select * from users_cumulated

insert into users_cumulated
with yesterday as (
select * from users_cumulated
where date = DATE('2023-01-01')
), today as(
 select 
 user_id::text as user_id,
 date(cast(event_time as timestamp)) as date_active
 from events 
 where date(cast(event_time as timestamp)) = DATE('2023-01-02')
 and user_id is not null
  group by user_id, date(cast(event_time as timestamp))
)
select 
coalesce(t.user_id,y.user_id) as user_id,
case when t.date_active is null then array[y.dates_active] 
else array[t.date_active]|| y.dates_active 
end as dates_active,
coalesce(t.date_active,y.date+ interval '1 day') as date
from yesterday y
full outer join today t 
on y.user_id = t.user_id


select * from users_cumulated




with users as (
select * from users_cumulated where date = date('2023-01-01')
),
series as (
select * from generate_series(date('2023-01-01'),date('2023-01-31'), interval '1 day') as series_date
)
select
case 
 when 
    dates_active @> array[date(series_date)]  
	then pow(2,32-date(series_date))
    else 0 
 end as  placeholder_int_value,*
from users cross join series 
where user_id = '137925124111668560' 
