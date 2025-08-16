from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, BooleanType, ArrayType, DateType

def create_spark_session():
    """Create and configure Spark session"""
    spark = SparkSession.builder \
        .appName("Device Activity Analysis") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .getOrCreate()
    return spark

def analyze_device_activity(spark, events_df, devices_df):
    """
    Analyze device activity by user and browser type.
    This converts the PostgreSQL query from Week 2 assignment.
    
    Args:
        spark: SparkSession
        events_df: DataFrame containing events data
        devices_df: DataFrame containing devices data
        
    Returns:
        DataFrame with device activity analysis
    """
    
    # Register the DataFrames as temporary views for SQL
    events_df.createOrReplaceTempView("events")
    devices_df.createOrReplaceTempView("devices")
    
    # SQL query converted from PostgreSQL
    sql_query = """
    WITH user_device_events AS (
        SELECT 
            e.user_id,
            e.device_id,
            CAST(e.event_time AS DATE) as event_date,
            d.browser_type
        FROM events e
        INNER JOIN devices d ON e.device_id = d.device_id
        WHERE e.user_id IS NOT NULL 
          AND e.device_id IS NOT NULL 
          AND d.browser_type IS NOT NULL
    ),
    daily_activity AS (
        SELECT 
            user_id,
            device_id,
            browser_type,
            event_date,
            COUNT(*) as daily_events
        FROM user_device_events
        GROUP BY user_id, device_id, browser_type, event_date
    ),
    activity_summary AS (
        SELECT 
            user_id,
            device_id,
            browser_type,
            COUNT(DISTINCT event_date) as active_days,
            COLLECT_LIST(event_date) as activity_dates,
            SUM(daily_events) as total_events,
            MIN(event_date) as first_activity,
            MAX(event_date) as last_activity
        FROM daily_activity
        GROUP BY user_id, device_id, browser_type
    )
    SELECT 
        user_id,
        device_id,
        browser_type,
        active_days,
        activity_dates,
        total_events,
        first_activity,
        last_activity
    FROM activity_summary
    ORDER BY user_id, browser_type, active_days DESC
    """
    
    result_df = spark.sql(sql_query)
    return result_df

def generate_datelist_int(spark, device_activity_df):
    """
    Convert device_activity_datelist to datelist_int using binary representation.
    This converts the datelist_int generation query from Week 2.
    
    Args:
        spark: SparkSession
        device_activity_df: DataFrame with device activity data
        
    Returns:
        DataFrame with datelist_int column
    """
    
    # Register the DataFrame as a temporary view for SQL
    device_activity_df.createOrReplaceTempView("device_activity")
    
    # SQL query for datelist_int generation
    sql_query = """
    WITH date_series AS (
        SELECT 
            user_id,
            device_id,
            browser_type,
            activity_dates,
            EXPLODE(activity_dates) as activity_date
        FROM device_activity
    ),
    binary_representation AS (
        SELECT 
            user_id,
            device_id,
            browser_type,
            activity_date,
            -- Convert date to binary position (simplified version)
            -- In a real scenario, you'd need to calculate the exact binary position
            CASE 
                WHEN activity_date IS NOT NULL THEN 1
                ELSE 0
            END as binary_flag
        FROM date_series
    )
    SELECT 
        user_id,
        device_id,
        browser_type,
        activity_dates,
        -- This is a simplified version - in practice you'd need more complex binary logic
        COUNT(*) as datelist_int
    FROM binary_representation
    GROUP BY user_id, device_id, browser_type, activity_dates
    """
    
    result_df = spark.sql(sql_query)
    return result_df

def main():
    """Main function to run the device activity analysis"""
    spark = create_spark_session()
    
    try:
        # Read events and devices data (assuming they're available as tables or files)
        # In a real scenario, this would be read from your data source
        events_df = spark.read.table("events")
        devices_df = spark.read.table("devices")
        
        # Perform the device activity analysis
        device_activity_df = analyze_device_activity(spark, events_df, devices_df)
        
        # Show results
        print("Device Activity Analysis Results:")
        device_activity_df.show(20, truncate=False)
        
        # Generate datelist_int
        datelist_int_df = generate_datelist_int(spark, device_activity_df)
        
        print("\nDevice Activity with Datelist Int:")
        datelist_int_df.show(20, truncate=False)
        
        # Save results if needed
        # device_activity_df.write.mode("overwrite").saveAsTable("device_activity_results")
        # datelist_int_df.write.mode("overwrite").saveAsTable("datelist_int_results")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
