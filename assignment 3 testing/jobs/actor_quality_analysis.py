from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, BooleanType, ArrayType

def create_spark_session():
    """Create and configure Spark session"""
    spark = SparkSession.builder \
        .appName("Actor Quality Analysis") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .getOrCreate()
    return spark

def analyze_actor_quality(spark, actor_films_df):
    """
    Analyze actor quality based on average ratings and categorize them.
    This converts the PostgreSQL query from Week 1 assignment.
    
    Args:
        spark: SparkSession
        actor_films_df: DataFrame containing actor_films data
        
    Returns:
        DataFrame with actor quality analysis
    """
    
    # Register the DataFrame as a temporary view for SQL
    actor_films_df.createOrReplaceTempView("actor_films")
    
    # SQL query converted from PostgreSQL
    sql_query = """
    WITH actor_aggregations AS (
        SELECT 
            actorid,
            actor,
            year,
            AVG(rating) as avg_rating,
            COUNT(*) as film_count,
            COLLECT_LIST(
                STRUCT(filmid, film, votes, rating)
            ) as movies
        FROM actor_films
        GROUP BY actorid, actor, year
    ),
    actor_quality AS (
        SELECT 
            actorid,
            actor,
            year,
            movies,
            film_count,
            avg_rating,
            CASE 
                WHEN avg_rating > 8 THEN 'star'
                WHEN avg_rating > 7 THEN 'good'
                WHEN avg_rating > 6 THEN 'average'
                WHEN avg_rating <= 6 THEN 'bad'
                ELSE 'unknown'
            END as quality_class,
            CASE 
                WHEN year = (SELECT MAX(year) FROM actor_films) THEN true
                ELSE false
            END as is_active
        FROM actor_aggregations
    )
    SELECT 
        actorid,
        actor,
        year,
        movies,
        film_count,
        avg_rating,
        quality_class,
        is_active
    FROM actor_quality
    ORDER BY actor, year DESC
    """
    
    result_df = spark.sql(sql_query)
    return result_df

def main():
    """Main function to run the actor quality analysis"""
    spark = create_spark_session()
    
    try:
        # Read actor_films data (assuming it's available as a table or file)
        # In a real scenario, this would be read from your data source
        actor_films_df = spark.read.table("actor_films")
        
        # Perform the analysis
        result_df = analyze_actor_quality(spark, actor_films_df)
        
        # Show results
        print("Actor Quality Analysis Results:")
        result_df.show(20, truncate=False)
        
        # Save results if needed
        # result_df.write.mode("overwrite").saveAsTable("actor_quality_results")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
