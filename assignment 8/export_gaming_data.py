#!/usr/bin/env python3
"""
Gaming Data Export Script for Tableau Dashboards
Exports match_details, matches, medals, and medals_matches_players data to CSV format
"""

import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import os

def export_gaming_data_to_csv():
    """
    Export gaming data from PostgreSQL database to CSV files for Tableau
    """
    
    # Database connection parameters
    # Updated with your Docker PostgreSQL credentials
    DB_PARAMS = {
        'host': 'localhost',
        'database': 'postgres',
        'user': 'postgres',
        'password': 'postgres',
        'port': '5432'
    }
    
    try:
        # Create database connection
        print("Connecting to database...")
        engine = create_engine(f"postgresql://{DB_PARAMS['user']}:{DB_PARAMS['password']}@{DB_PARAMS['host']}:{DB_PARAMS['port']}/{DB_PARAMS['database']}")
        
        # Create data directory if it doesn't exist
        os.makedirs('gaming_data_csv', exist_ok=True)
        
        # Export each table to CSV
        tables_to_export = [
            'medals',
            'match_details', 
            'matches',
            'medals_matches_players'
        ]
        
        for table_name in tables_to_export:
            print(f"Exporting {table_name}...")
            
            # Read data from database
            query = f"SELECT * FROM {table_name}"
            df = pd.read_sql(query, engine)
            
            # Export to CSV
            csv_path = f"gaming_data_csv/{table_name}.csv"
            df.to_csv(csv_path, index=False)
            
            print(f"✓ {table_name} exported to {csv_path}")
            print(f"  - Rows: {len(df)}")
            print(f"  - Columns: {len(df.columns)}")
            print(f"  - File size: {os.path.getsize(csv_path) / 1024:.1f} KB")
            print()
        
        print("🎉 All data exported successfully!")
        print("📁 CSV files are ready in the 'gaming_data_csv' folder")
        print("🚀 You can now import these files into Tableau")
        
    except Exception as e:
        print(f"❌ Error exporting data: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Check your database connection parameters")
        print("2. Ensure the database is running")
        print("3. Verify table names exist in your database")
        print("4. Check user permissions")

def create_sample_data():
    """
    Create sample gaming data if database connection fails
    """
    print("Creating sample gaming data...")
    
    # Create sample medals data
    medals_data = {
        'medal_id': range(1, 11),
        'medal_name': ['Killing Spree', 'Double Kill', 'Triple Kill', 'Quadra Kill', 'Penta Kill', 
                       'First Blood', 'Assist Master', 'Survivor', 'MVP', 'Team Player'],
        'medal_description': ['5 kills in a row', '2 kills in quick succession', '3 kills in quick succession',
                             '4 kills in quick succession', '5 kills in quick succession', 'First kill of the match',
                             'Most assists in match', 'Survived longest', 'Most valuable player', 'Best team player'],
        'points': [100, 50, 75, 150, 300, 25, 40, 60, 200, 80]
    }
    
    # Create sample matches data
    matches_data = {
        'match_id': range(1, 101),
        'map_name': ['Summoner\'s Rift', 'Howling Abyss', 'Twisted Treeline'] * 33 + ['Summoner\'s Rift'],
        'playlist': ['Ranked Solo', 'Ranked Flex', 'Normal Draft', 'Normal Blind', 'ARAM'] * 20,
        'match_duration': [1200, 1800, 1500, 2100, 1600] * 20,
        'winner': ['Team A', 'Team B'] * 50,
        'match_date': pd.date_range('2024-01-01', periods=100, freq='D')
    }
    
    # Create sample match_details data
    match_details_data = {
        'match_id': [i for i in range(1, 101) for _ in range(10)],  # 10 players per match
        'player_id': [f'player_{i:03d}' for i in range(1, 1001)],
        'player_name': [f'Player{i:03d}' for i in range(1, 1001)],
        'kills': [np.random.randint(0, 20) for _ in range(1000)],
        'deaths': [np.random.randint(0, 15) for _ in range(1000)],
        'assists': [np.random.randint(0, 25) for _ in range(1000)],
        'damage_dealt': [np.random.randint(5000, 50000) for _ in range(1000)],
        'damage_taken': [np.random.randint(3000, 40000) for _ in range(1000)]
    }
    
    # FIXED: Create medals_matches_players with consistent player IDs
    medals_matches_players_data = []
    
    for match_id in range(1, 101):
        # Get the 10 players who actually played in this match
        match_start_player = (match_id - 1) * 10 + 1
        match_players = [f'player_{i:03d}' for i in range(match_start_player, match_start_player + 10)]
        
        # Assign 5 medals to players from this match (meaningful relationships)
        for _ in range(5):
            # Randomly select a player who actually played in this match
            selected_player = np.random.choice(match_players)
            # Randomly select a medal
            selected_medal = np.random.randint(1, 11)
            # Create timestamp for this match
            match_date = pd.Timestamp('2024-01-01') + pd.Timedelta(days=match_id-1)
            earned_time = match_date + pd.Timedelta(hours=np.random.randint(0, 24))
            
            medals_matches_players_data.append({
                'match_id': match_id,
                'player_id': selected_player,
                'medal_id': selected_medal,
                'earned_at': earned_time
            })
    
    # Create DataFrames
    medals_df = pd.DataFrame(medals_data)
    matches_df = pd.DataFrame(matches_data)
    match_details_df = pd.DataFrame(match_details_data)
    medals_matches_players_df = pd.DataFrame(medals_matches_players_data)
    
    # Create data directory
    os.makedirs('gaming_data_csv', exist_ok=True)
    
    # Export to CSV
    medals_df.to_csv('gaming_data_csv/medals.csv', index=False)
    matches_df.to_csv('gaming_data_csv/matches.csv', index=False)
    match_details_df.to_csv('gaming_data_csv/match_details.csv', index=False)
    medals_matches_players_df.to_csv('gaming_data_csv/medals_matches_players.csv', index=False)
    
    print("✅ Sample gaming data created successfully!")
    print("📁 CSV files are ready in the 'gaming_data_csv' folder")
    
    # Verify data consistency
    print("\n🔍 Data Consistency Check:")
    print(f"Total matches: {len(matches_df)}")
    print(f"Total players in matches: {len(match_details_df)}")
    print(f"Total medal awards: {len(medals_matches_players_df)}")
    
    # Check player ID consistency for first few matches
    for match_id in [1, 2, 3]:
        match_players = set(match_details_df[match_details_df['match_id'] == match_id]['player_id'])
        match_medals = set(medals_matches_players_df[medals_matches_players_df['match_id'] == match_id]['player_id'])
        common_players = match_players.intersection(match_medals)
        print(f"Match {match_id}: {len(common_players)} players with medals out of {len(match_players)} total players")

if __name__ == "__main__":
    print("🎮 Gaming Data Export for Tableau Dashboards")
    print("=" * 50)
    
    # Since the database tables don't exist, create sample data directly
    print("Creating sample gaming data for Tableau...")
    import numpy as np
    create_sample_data()
    
    print("\n📊 Next Steps:")
    print("1. Open Tableau Public")
    print("2. Import the CSV files from 'gaming_data_csv' folder")
    print("3. Create your executive and exploratory dashboards")
    print("4. Publish to Tableau Public")
    print("5. Submit the dashboard links")
