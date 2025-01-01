drop table fct_game_details
create table fct_game_details (
dim_game_date date,
dim_season integer,
dim_team_id integer,
dim_player_id integer,
dim_player_name text,
dim_start_position text,
dim_is_playing_at_home boolean,
dim_did_not_play boolean,
dim_did_not_dress boolean,
dim_not_with_team boolean,
m_minutes real,
m_fgm integer,
m_fga integer,
m_fg3m integer,
m_fg3a integer,
m_ftm integer,
m_fta integer,
m_oreb integer,
m_dreb integer,
m_reb integer,
m_ast integer,
m_stl integer,
m_blk integer,
m_turnovers integer,
m_pf integer,
m_pts integer,
m_plus_minus integer,
primary key(dim_game_date,dim_team_id,dim_player_id)
)


insert into fct_game_details
with deduped as (
select 
g.game_date_est,
g.season,
g.home_team_id,
g.visitor_team_id,
gd.*, 
row_number() over (partition by player_id, gd.game_id, team_id order by g.game_date_est) as row_num 
from game_details gd
join games g on gd.game_id = g.game_id
)
select 
game_date_est as dim_game_date,
season as dim_season,
team_id as dim_team_id,
player_id as dim_player_id,
player_name as dim_player_name,
start_position as dim_start_position,
team_id = home_team_id as dim_is_playing_at_home,
coalesce(position('DNP' in comment),0)>0 as dim_did_not_play,
coalesce(position('DND' in comment),0)>0 as dim_did_not_dress,
coalesce(position('NWT' in comment),0)>0 as dim_not_with_team,
cast(split_part(min,':',1) as real)+cast(split_part(min,':',2) as real)/60 as m_minutes,
fgm AS m_fgm,
fga AS m_fga,
fg3m AS m_fg3m,
fg3a AS m_fg3a,
ftm AS m_ftm, 
fta AS m_fta,
oreb AS m_oreb, 
dreb AS m_dreb,
reb AS m_reb,
ast AS m_ast, 
stl AS m_stl,
blk AS m_blk, 
"TO" AS m_Turnovers,
pf AS m_pf,
pts AS m_pts,
plus_minus as m_plus_minus
from deduped
where row_num =1


select * from fct_game_details


select* from game_details




SELECT dim_player_name,
       dim_is_playing_at_home,
       COUNT(1) AS num_games,
       SUM(m_pts) AS total_points,
       COUNT(CASE WHEN dim_not_with_team THEN 1 END) AS bailed_num,
       CAST(COUNT(CASE WHEN dim_not_with_team THEN 1 END) AS REAL)/COUNT(1) AS bail_num
FROM fct_game_details
GROUP BY 1,2
ORDER BY 6 DESC;
