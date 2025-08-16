import os
import traceback
import psycopg2
from datetime import datetime, timedelta
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import EnvironmentSettings, DataTypes, TableEnvironment, StreamTableEnvironment
from pyflink.table.expressions import lit, col
from pyflink.table.window import Session
import json

def get_postgres_connection():
    """Get PostgreSQL connection"""
    try:
        conn = psycopg2.connect(
            host="host.docker.internal",
            database="postgres",
            user="postgres",
            password="postgres"
        )
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

def read_tech_creator_events():
    """Read Tech Creator events from PostgreSQL"""
    conn = get_postgres_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        
        # Query to get Tech Creator events
        query = """
        SELECT ip, event_timestamp, host, url, referrer, geodata
        FROM processed_events 
        WHERE host LIKE '%techcreator.io' 
           OR host LIKE '%zachwilson.tech' 
           OR host LIKE '%lulu.techcreator.io'
        ORDER BY ip, event_timestamp
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Convert to list of dictionaries
        events = []
        for row in rows:
            events.append({
                'ip': row[0],
                'event_timestamp': row[1],
                'host': row[2],
                'url': row[3],
                'referrer': row[4],
                'geodata': row[5]
            })
        
        print(f"Found {len(events)} Tech Creator events")
        return events
        
    except Exception as e:
        print(f"Error reading events: {e}")
        return []
    finally:
        conn.close()

def sessionize_events(events, gap_minutes=5):
    """Sessionize events with specified gap in minutes"""
    if not events:
        return []
    
    # Sort events by IP, host, and timestamp
    sorted_events = sorted(events, key=lambda x: (x['ip'], x['host'], x['event_timestamp']))
    
    sessions = []
    current_session = None
    
    for event in sorted_events:
        if current_session is None:
            # Start new session
            current_session = {
                'host': event['host'],
                'ip': event['ip'],
                'session_start': event['event_timestamp'],
                'session_end': event['event_timestamp'],
                'events': [event]
            }
        else:
            # Check if this event belongs to current session
            time_diff = event['event_timestamp'] - current_session['session_end']
            gap_threshold = timedelta(minutes=gap_minutes)
            
            if (event['ip'] == current_session['ip'] and 
                event['host'] == current_session['host'] and 
                time_diff <= gap_threshold):
                # Extend current session
                current_session['session_end'] = event['event_timestamp']
                current_session['events'].append(event)
            else:
                # Close current session and start new one
                sessions.append(current_session)
                current_session = {
                    'host': event['host'],
                    'ip': event['ip'],
                    'session_start': event['event_timestamp'],
                    'session_end': event['event_timestamp'],
                    'events': [event]
                }
    
    # Add the last session
    if current_session:
        sessions.append(current_session)
    
    return sessions

def calculate_session_metrics(sessions):
    """Calculate metrics for each session"""
    session_results = []
    host_summary = {}
    
    for session in sessions:
        # Calculate session duration
        duration = session['session_end'] - session['session_start']
        duration_minutes = duration.total_seconds() / 60
        
        # Create session result
        session_result = {
            'host': session['host'],
            'ip': session['ip'],
            'session_start': session['session_start'],
            'session_end': session['session_end'],
            'num_events': len(session['events']),
            'session_duration_minutes': duration_minutes
        }
        session_results.append(session_result)
        
        # Update host summary
        host = session['host']
        if host not in host_summary:
            host_summary[host] = {
                'total_sessions': 0,
                'total_events': 0,
                'total_duration': 0
            }
        
        host_summary[host]['total_sessions'] += 1
        host_summary[host]['total_events'] += len(session['events'])
        host_summary[host]['total_duration'] += duration_minutes
    
    # Calculate averages for host summary
    host_summary_results = []
    for host, stats in host_summary.items():
        avg_events = stats['total_events'] / stats['total_sessions']
        avg_duration = stats['total_duration'] / stats['total_sessions']
        
        host_summary_results.append({
            'host': host,
            'total_sessions': stats['total_sessions'],
            'avg_events_per_session': avg_events,
            'avg_session_duration_minutes': avg_duration,
            'total_events': stats['total_events']
        })
    
    return session_results, host_summary_results

def write_results_to_postgres(session_results, host_summary_results):
    """Write results back to PostgreSQL"""
    conn = get_postgres_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("TRUNCATE tech_creator_sessions, tech_creator_host_summary")
        
        # Insert session results
        for session in session_results:
            cursor.execute("""
                INSERT INTO tech_creator_sessions 
                (host, ip, session_start, session_end, num_events, session_duration_minutes)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                session['host'], session['ip'], session['session_start'], 
                session['session_end'], session['num_events'], session['session_duration_minutes']
            ))
        
        # Insert host summary results
        for summary in host_summary_results:
            cursor.execute("""
                INSERT INTO tech_creator_host_summary 
                (host, total_sessions, avg_events_per_session, avg_session_duration_minutes, total_events)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                summary['host'], summary['total_sessions'], summary['avg_events_per_session'],
                summary['avg_session_duration_minutes'], summary['total_events']
            ))
        
        conn.commit()
        print(f"Successfully wrote {len(session_results)} sessions and {len(host_summary_results)} host summaries")
        return True
        
    except Exception as e:
        print(f"Error writing to PostgreSQL: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def run_tech_creator_session_analysis():
    """Main function to run the Tech Creator sessionization analysis"""
    
    try:
        print("Starting Tech Creator sessionization analysis...")
        
        # Step 1: Read events from PostgreSQL
        print("Reading Tech Creator events from PostgreSQL...")
        events = read_tech_creator_events()
        
        if not events:
            print("No Tech Creator events found!")
            return
        
        # Step 2: Sessionize events with 5-minute gap
        print("Sessionizing events with 5-minute gap...")
        sessions = sessionize_events(events, gap_minutes=5)
        
        if not sessions:
            print("No sessions created!")
            return
        
        print(f"Created {len(sessions)} sessions")
        
        # Step 3: Calculate metrics
        print("Calculating session metrics...")
        session_results, host_summary_results = calculate_session_metrics(sessions)
        
        # Step 4: Write results back to PostgreSQL
        print("Writing results to PostgreSQL...")
        success = write_results_to_postgres(session_results, host_summary_results)
        
        if success:
            print("Tech Creator sessionization analysis completed successfully!")
            print(f"\nResults:")
            print(f"- Total sessions: {len(session_results)}")
            print(f"- Hosts analyzed: {len(host_summary_results)}")
            
            print("\nTo answer your homework questions, run these SQL queries:")
            print("\n1. Average events per session for Tech Creator users:")
            print("""
            SELECT 
                host,
                ROUND(avg_events_per_session, 2) as avg_events_per_session,
                total_sessions,
                total_events
            FROM tech_creator_host_summary
            ORDER BY avg_events_per_session DESC;
            """)
            
            print("\n2. Compare results between different hosts:")
            print("""
            WITH overall_avg AS (
                SELECT AVG(avg_events_per_session) as overall_avg_events
                FROM tech_creator_host_summary
            )
            SELECT 
                h.host,
                ROUND(h.avg_events_per_session, 2) as avg_events_per_session,
                h.total_sessions,
                ROUND(o.overall_avg_events, 2) as overall_avg,
                CASE 
                    WHEN h.avg_events_per_session > o.overall_avg_events THEN 'Above Average'
                    ELSE 'Below Average'
                END as performance
            FROM tech_creator_host_summary h, overall_avg o
            ORDER BY h.avg_events_per_session DESC;
            """)
        else:
            print("Failed to write results to PostgreSQL")
            
    except Exception as e:
        print(f"Error in Tech Creator sessionization analysis: {str(e)}")
        traceback.print_exc()

if __name__ == '__main__':
    run_tech_creator_session_analysis()
