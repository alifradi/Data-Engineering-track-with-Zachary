import os
import traceback
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import EnvironmentSettings, DataTypes, TableEnvironment, StreamTableEnvironment
from pyflink.table.expressions import lit, col


from pyflink.table.window import Session
import json


def create_postgres_source_table(t_env):
    """Create source table reading from PostgreSQL processed_events"""
    table_name = 'web_events_source'
    source_ddl = f"""
        CREATE TABLE {table_name} (
            ip VARCHAR,
            event_timestamp TIMESTAMP(3),
            referrer VARCHAR,
            host VARCHAR,
            url VARCHAR,
            geodata VARCHAR,
            WATERMARK FOR event_timestamp AS event_timestamp - INTERVAL '1' MINUTE
        ) WITH (
            'connector' = 'jdbc',
            'url' = '{os.environ.get("POSTGRES_URL")}',
            'table-name' = 'processed_events',
            'username' = '{os.environ.get("POSTGRES_USER", "postgres")}',
            'password' = '{os.environ.get("POSTGRES_PASSWORD", "postgres")}',
            'driver' = 'org.postgresql.Driver',
            'scan.fetch-size' = '1000'
        );
    """
    t_env.execute_sql(source_ddl)
    return table_name


def create_session_results_sink(t_env):
    """Create sink table for session results"""
    table_name = 'tech_creator_sessions'
    sink_ddl = f"""
        CREATE TABLE {table_name} (
            host VARCHAR,
            ip VARCHAR,
            session_start TIMESTAMP(3),
            session_end TIMESTAMP(3),
            num_events BIGINT,
            session_duration_minutes DOUBLE PRECISION,
            PRIMARY KEY (host, ip, session_start) NOT ENFORCED
        ) WITH (
            'connector' = 'jdbc',
            'url' = '{os.environ.get("POSTGRES_URL")}',
            'table-name' = '{table_name}',
            'username' = '{os.environ.get("POSTGRES_USER", "postgres")}',
            'password' = '{os.environ.get("POSTGRES_PASSWORD", "postgres")}',
            'driver' = 'org.postgresql.Driver'
        );
    """
    t_env.execute_sql(sink_ddl)
    return table_name


def create_host_summary_sink(t_env):
    """Create sink table for host summary statistics"""
    table_name = 'tech_creator_host_summary'
    sink_ddl = f"""
        CREATE TABLE {table_name} (
            host VARCHAR,
            total_sessions BIGINT,
            avg_events_per_session DOUBLE PRECISION,
            avg_session_duration_minutes DOUBLE PRECISION,
            total_events BIGINT,
            PRIMARY KEY (host) NOT ENFORCED
        ) WITH (
            'connector' = 'jdbc',
            'url' = '{os.environ.get("POSTGRES_URL")}',
            'table-name' = '{table_name}',
            'username' = '{os.environ.get("POSTGRES_USER", "postgres")}',
            'password' = '{os.environ.get("POSTGRES_PASSWORD", "postgres")}',
            'driver' = 'org.postgresql.Driver'
        );
    """
    t_env.execute_sql(sink_ddl)
    return table_name


def run_tech_creator_session_analysis():
    """Main function to run the Tech Creator sessionization analysis"""
    
    # Set up the execution environment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.enable_checkpointing(10)
    env.set_parallelism(3)

    # Set up the table environment
    settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
    t_env = StreamTableEnvironment.create(env, environment_settings=settings)
    
    # Debug: Check environment variables
    print(f"POSTGRES_URL: {os.environ.get('POSTGRES_URL', 'NOT SET')}")
    print(f"POSTGRES_USER: {os.environ.get('POSTGRES_USER', 'NOT SET')}")
    print(f"POSTGRES_PASSWORD: {os.environ.get('POSTGRES_PASSWORD', 'NOT SET')}")
    
    # Set default values if not present
    if not os.environ.get('POSTGRES_URL'):
        os.environ['POSTGRES_URL'] = 'jdbc:postgresql://my-postgres-container:5432/postgres'
    if not os.environ.get('POSTGRES_USER'):
        os.environ['POSTGRES_USER'] = 'postgres'
    if not os.environ.get('POSTGRES_PASSWORD'):
        os.environ['POSTGRES_PASSWORD'] = 'postgres'

    try:
        print("Starting Tech Creator sessionization analysis...")
        
        # Create source and sink tables
        source_table = create_postgres_source_table(t_env)
        session_sink = create_session_results_sink(t_env)
        summary_sink = create_host_summary_sink(t_env)

        # Filter for Tech Creator hosts and apply 5-minute sessionization
        tech_creator_sessions = t_env.from_path(source_table)\
            .filter(
                (col("host").like("%techcreator.io")) | 
                (col("host").like("%zachwilson.tech")) |
                (col("host").like("%lulu.techcreator.io"))
            )\
            .window(
                Session.with_gap(lit(5).minutes).on(col("event_timestamp")).alias("session_window")
            )\
            .group_by(
                col("session_window"),
                col("host"),
                col("ip")
            )\
            .select(
                col("host"),
                col("ip"),
                col("session_window").start.alias("session_start"),
                col("session_window").end.alias("session_end"),
                lit(1).count.alias("num_events"),
                lit(0.0).alias("session_duration_minutes")
            )

        # Write session results
        tech_creator_sessions.execute_insert(session_sink)

        # Calculate host summary statistics
        host_summary = tech_creator_sessions\
            .group_by(col("host"))\
            .select(
                col("host"),
                lit(1).count.alias("total_sessions"),
                col("num_events").avg.alias("avg_events_per_session"),
                col("session_duration_minutes").avg.alias("avg_session_duration_minutes"),
                col("num_events").sum.alias("total_events")
            )

        # Write host summary
        host_summary.execute_insert(summary_sink)

        print("Tech Creator sessionization analysis completed successfully!")
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

        # The job will execute automatically when we call execute_insert
        print("Job execution started...")
        print("Waiting for job to complete...")
        
        # Force execution by collecting results (this will trigger the job)
        try:
            # This will force the job to execute
            session_count = tech_creator_sessions.count()
            print(f"Session count: {session_count}")
        except Exception as e:
            print(f"Note: {e}")
            print("Job may still be processing in background...")

    except Exception as e:
        print(f"Error in Tech Creator sessionization analysis: {str(e)}")
        traceback.print_exc()


if __name__ == '__main__':
    run_tech_creator_session_analysis()
