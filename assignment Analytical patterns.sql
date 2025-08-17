-- Assignment 4: Applying Analytical Patterns
-- Week 4 Homework - Using players, players_scd, and player_seasons tables from week 1

-- ============================================================================
-- 1. STATE CHANGE TRACKING FOR PLAYERS
-- ============================================================================

-- This query tracks state changes for players based on their activity status
-- States: New, Retired, Continued Playing, Returned from Retirement, Stayed Retired

WITH player_state_changes AS (
    SELECT 
        p.player_id,
        p.player_name,
        psc.season,
        psc.is_active,
        psc.quality_class,
        -- Previous season's status
        LAG(psc.is_active, 1) OVER (PARTITION BY p.player_id ORDER BY psc.season) AS prev_is_active,
        -- Next season's status  
        LEAD(psc.is_active, 1) OVER (PARTITION BY p.player_id ORDER BY psc.season) AS next_is_active,
        -- First season for this player
        FIRST_VALUE(psc.season) OVER (PARTITION BY p.player_id ORDER BY psc.season) AS first_season,
        -- Last season for this player
        LAST_VALUE(psc.season) OVER (PARTITION BY p.player_id ORDER BY psc.season ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_season
    FROM players p
    JOIN players_scd psc ON p.player_id = psc.player_id
),
player_states AS (
    SELECT 
        *,
        CASE 
            -- Player entering the league
            WHEN season = first_season AND is_active = true THEN 'New'
            -- Player leaving the league
            WHEN season = last_season AND is_active = false AND prev_is_active = true THEN 'Retired'
            -- Player staying in the league
            WHEN is_active = true AND prev_is_active = true THEN 'Continued Playing'
            -- Player returning from retirement
            WHEN is_active = true AND prev_is_active = false THEN 'Returned from Retirement'
            -- Player staying out of the league
            WHEN is_active = false AND prev_is_active = false THEN 'Stayed Retired'
            ELSE 'Unknown'
        END AS player_state
    FROM player_state_changes
)
SELECT 
    player_id,
    player_name,
    season,
    is_active,
    quality_class,
    player_state
FROM player_states
ORDER BY player_id, season;

-- ============================================================================
-- 2. GROUPING SETS AGGREGATIONS FOR GAME_DETAILS
-- ============================================================================

-- This query uses GROUPING SETS to efficiently aggregate game_details data
-- along multiple dimensions: player+team, player+season, and team

WITH game_aggregations AS (
    SELECT 
        COALESCE(player_id, 'ALL_PLAYERS') AS player_id,
        COALESCE(player_name, 'ALL_PLAYERS') AS player_name,
        COALESCE(team_id, 'ALL_TEAMS') AS team_id,
        COALESCE(team_name, 'ALL_TEAMS') AS team_name,
        COALESCE(season, 'ALL_SEASONS') AS season,
        COUNT(*) AS games_played,
        SUM(points) AS total_points,
        AVG(points) AS avg_points,
        SUM(rebounds) AS total_rebounds,
        AVG(rebounds) AS avg_rebounds,
        SUM(assists) AS total_assists,
        AVG(assists) AS avg_assists,
        SUM(CASE WHEN team_score > opponent_score THEN 1 ELSE 0 END) AS wins,
        SUM(CASE WHEN team_score < opponent_score THEN 1 ELSE 0 END) AS losses,
        -- GROUPING function to identify which dimension each row represents
        GROUPING(player_id, team_id, season) AS grouping_id
    FROM game_details
    GROUP BY GROUPING SETS (
        (player_id, player_name, team_id, team_name, season),  -- player + team + season
        (player_id, player_name, team_id, team_name),          -- player + team
        (player_id, player_name, season),                      -- player + season
        (team_id, team_name),                                  -- team only
        ()                                                     -- grand total
    )
)
SELECT 
    player_id,
    player_name,
    team_id,
    team_name,
    season,
    games_played,
    total_points,
    ROUND(avg_points, 2) AS avg_points,
    total_rebounds,
    ROUND(avg_rebounds, 2) AS avg_rebounds,
    total_assists,
    ROUND(avg_assists, 2) AS avg_assists,
    wins,
    losses,
    CASE 
        WHEN grouping_id = 0 THEN 'Player + Team + Season'
        WHEN grouping_id = 1 THEN 'Player + Team'
        WHEN grouping_id = 2 THEN 'Player + Season'
        WHEN grouping_id = 3 THEN 'Team Only'
        WHEN grouping_id = 7 THEN 'Grand Total'
        ELSE 'Unknown'
    END AS aggregation_level
FROM game_aggregations
ORDER BY 
    CASE 
        WHEN grouping_id = 0 THEN 1
        WHEN grouping_id = 1 THEN 2
        WHEN grouping_id = 2 THEN 3
        WHEN grouping_id = 3 THEN 4
        WHEN grouping_id = 7 THEN 5
    END,
    total_points DESC;

-- ============================================================================
-- 3. WINDOW FUNCTIONS FOR STREAK ANALYSIS
-- ============================================================================

-- Query 1: Most games a team has won in a 90-game stretch
WITH team_win_streaks AS (
    SELECT 
        team_id,
        team_name,
        game_date,
        CASE WHEN team_score > opponent_score THEN 1 ELSE 0 END AS is_win,
        -- Rolling sum of wins over 90 games
        SUM(CASE WHEN team_score > opponent_score THEN 1 ELSE 0 END) 
            OVER (PARTITION BY team_id ORDER BY game_date ROWS BETWEEN 89 PRECEDING AND CURRENT ROW) AS wins_in_90_games,
        -- Rolling count of games in the 90-game window
        COUNT(*) OVER (PARTITION BY team_id ORDER BY game_date ROWS BETWEEN 89 PRECEDING AND CURRENT ROW) AS games_in_window
    FROM game_details
),
max_win_streaks AS (
    SELECT 
        team_id,
        team_name,
        MAX(wins_in_90_games) AS max_wins_in_90_games,
        AVG(wins_in_90_games) AS avg_wins_in_90_games
    FROM team_win_streaks
    WHERE games_in_window = 90  -- Only consider complete 90-game windows
    GROUP BY team_id, team_name
)
SELECT 
    team_id,
    team_name,
    max_wins_in_90_games,
    ROUND(avg_wins_in_90_games, 2) AS avg_wins_in_90_games,
    ROUND(max_wins_in_90_games / 90.0 * 100, 2) AS max_win_percentage
FROM max_win_streaks
ORDER BY max_wins_in_90_games DESC;

-- Query 2: How many games in a row did LeBron James score over 10 points?
WITH lebron_scoring_streaks AS (
    SELECT 
        player_id,
        player_name,
        game_date,
        points,
        CASE WHEN points > 10 THEN 1 ELSE 0 END AS scored_over_10,
        -- Create groups for consecutive games with over 10 points
        SUM(CASE WHEN points <= 10 THEN 1 ELSE 0 END) 
            OVER (PARTITION BY player_id ORDER BY game_date) AS streak_group
    FROM game_details
    WHERE player_name = 'LeBron James'
),
streak_lengths AS (
    SELECT 
        player_id,
        player_name,
        streak_group,
        COUNT(*) AS consecutive_games_over_10
    FROM lebron_scoring_streaks
    WHERE scored_over_10 = 1
    GROUP BY player_id, player_name, streak_group
)
SELECT 
    player_name,
    MAX(consecutive_games_over_10) AS max_consecutive_games_over_10,
    AVG(consecutive_games_over_10) AS avg_consecutive_games_over_10,
    COUNT(*) AS total_streaks_over_10
FROM streak_lengths
GROUP BY player_id, player_name;

-- ============================================================================
-- 4. ADDITIONAL ANALYTICAL QUERIES
-- ============================================================================

-- Top 10 players by total points for a single team
SELECT 
    player_id,
    player_name,
    team_id,
    team_name,
    SUM(points) AS total_points,
    COUNT(*) AS games_played,
    ROUND(AVG(points), 2) AS avg_points_per_game
FROM game_details
GROUP BY player_id, player_name, team_id, team_name
ORDER BY total_points DESC
LIMIT 10;

-- Top 10 players by total points in a single season
SELECT 
    player_id,
    player_name,
    season,
    SUM(points) AS total_points,
    COUNT(*) AS games_played,
    ROUND(AVG(points), 2) AS avg_points_per_game
FROM game_details
GROUP BY player_id, player_name, season
ORDER BY total_points DESC
LIMIT 10;

-- Team performance ranking by win percentage
SELECT 
    team_id,
    team_name,
    COUNT(*) AS total_games,
    SUM(CASE WHEN team_score > opponent_score THEN 1 ELSE 0 END) AS wins,
    SUM(CASE WHEN team_score < opponent_score THEN 1 ELSE 0 END) AS losses,
    ROUND(
        SUM(CASE WHEN team_score > opponent_score THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 
        2
    ) AS win_percentage
FROM game_details
GROUP BY team_id, team_name
ORDER BY win_percentage DESC;

-- ============================================================================
-- END OF ASSIGNMENT 4 QUERIES
-- ============================================================================
