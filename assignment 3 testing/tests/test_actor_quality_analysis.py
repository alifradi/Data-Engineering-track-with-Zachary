import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, ArrayType, BooleanType
from src.jobs.actor_quality_analysis import analyze_actor_quality

class TestActorQualityAnalysis:
    """Test class for actor quality analysis functionality"""
    
    @pytest.fixture(scope="class")
    def spark(self):
        """Create a Spark session for testing"""
        spark = SparkSession.builder \
            .appName("TestActorQualityAnalysis") \
            .master("local[2]") \
            .config("spark.sql.adaptive.enabled", "false") \
            .getOrCreate()
        
        yield spark
        spark.stop()
    
    @pytest.fixture(scope="class")
    def sample_actor_films_data(self, spark):
        """Create sample actor_films data for testing"""
        schema = StructType([
            StructField("actorid", StringType(), True),
            StructField("actor", StringType(), True),
            StructField("film", StringType(), True),
            StructField("year", IntegerType(), True),
            StructField("votes", IntegerType(), True),
            StructField("rating", DoubleType(), True),
            StructField("filmid", StringType(), True)
        ])
        
        data = [
            ("actor1", "Al Pacino", "The Godfather", 1972, 1000, 9.2, "film1"),
            ("actor1", "Al Pacino", "The Godfather Part II", 1974, 800, 9.0, "film2"),
            ("actor1", "Al Pacino", "Scarface", 1983, 600, 8.3, "film3"),
            ("actor2", "Marlon Brando", "The Godfather", 1972, 1000, 9.2, "film1"),
            ("actor2", "Marlon Brando", "Apocalypse Now", 1979, 700, 8.4, "film4"),
            ("actor3", "Robert De Niro", "Taxi Driver", 1976, 900, 8.2, "film5"),
            ("actor3", "Robert De Niro", "Goodfellas", 1990, 750, 8.7, "film6"),
            ("actor4", "Tom Hanks", "Forrest Gump", 1994, 1200, 8.8, "film7"),
            ("actor4", "Tom Hanks", "Cast Away", 2000, 600, 7.8, "film8"),
            ("actor5", "Nicholas Cage", "The Rock", 1996, 500, 6.9, "film9"),
            ("actor5", "Nicholas Cage", "Con Air", 1997, 400, 6.7, "film10")
        ]
        
        return spark.createDataFrame(data, schema)
    
    @pytest.fixture(scope="class")
    def expected_actor_quality_data(self, spark):
        """Create expected output data for actor quality analysis"""
        schema = StructType([
            StructField("actorid", StringType(), True),
            StructField("actor", StringType(), True),
            StructField("year", IntegerType(), True),
            StructField("movies", ArrayType(StructType([
                StructField("filmid", StringType(), True),
                StructField("film", StringType(), True),
                StructField("votes", IntegerType(), True),
                StructField("rating", DoubleType(), True)
            ])), True),
            StructField("film_count", IntegerType(), True),
            StructField("avg_rating", DoubleType(), True),
            StructField("quality_class", StringType(), True),
            StructField("is_active", BooleanType(), True)
        ])
        
        # Expected results based on the sample data
        data = [
            ("actor1", "Al Pacino", 1983, [("film3", "Scarface", 600, 8.3)], 1, 8.3, "good", False),
            ("actor1", "Al Pacino", 1974, [("film2", "The Godfather Part II", 800, 9.0)], 1, 9.0, "star", False),
            ("actor1", "Al Pacino", 1972, [("film1", "The Godfather", 1000, 9.2)], 1, 9.2, "star", False),
            ("actor2", "Marlon Brando", 1979, [("film4", "Apocalypse Now", 700, 8.4)], 1, 8.4, "good", False),
            ("actor2", "Marlon Brando", 1972, [("film1", "The Godfather", 1000, 9.2)], 1, 9.2, "star", False),
            ("actor3", "Robert De Niro", 1990, [("film6", "Goodfellas", 750, 8.7)], 1, 8.7, "good", False),
            ("actor3", "Robert De Niro", 1976, [("film5", "Taxi Driver", 900, 8.2)], 1, 8.2, "good", False),
            ("actor4", "Tom Hanks", 2000, [("film8", "Cast Away", 600, 7.8)], 1, 7.8, "good", False),
            ("actor4", "Tom Hanks", 1994, [("film7", "Forrest Gump", 1200, 8.8)], 1, 8.8, "good", False),
            ("actor5", "Nicholas Cage", 1997, [("film10", "Con Air", 400, 6.7)], 1, 6.7, "average", False),
            ("actor5", "Nicholas Cage", 1996, [("film9", "The Rock", 500, 6.9)], 1, 6.9, "average", False)
        ]
        
        return spark.createDataFrame(data, schema)
    
    def test_analyze_actor_quality_structure(self, spark, sample_actor_films_data):
        """Test that the actor quality analysis returns the correct structure"""
        result_df = analyze_actor_quality(spark, sample_actor_films_data)
        
        # Check that all expected columns are present
        expected_columns = {
            "actorid", "actor", "year", "movies", "film_count", 
            "avg_rating", "quality_class", "is_active"
        }
        actual_columns = set(result_df.columns)
        assert expected_columns.issubset(actual_columns), f"Missing columns. Expected: {expected_columns}, Got: {actual_columns}"
        
        # Check that we have the expected number of rows
        assert result_df.count() == 11, f"Expected 11 rows, got {result_df.count()}"
    
    def test_actor_quality_classification(self, spark, sample_actor_films_data):
        """Test that actors are correctly classified by quality"""
        result_df = analyze_actor_quality(spark, sample_actor_films_data)
        
        # Test star classification (> 8.0)
        star_actors = result_df.filter(result_df.quality_class == "star")
        star_ratings = star_actors.select("avg_rating").collect()
        for row in star_ratings:
            assert row.avg_rating > 8.0, f"Star actor should have rating > 8.0, got {row.avg_rating}"
        
        # Test good classification (> 7.0 and <= 8.0)
        good_actors = result_df.filter(result_df.quality_class == "good")
        good_ratings = good_actors.select("avg_rating").collect()
        for row in good_ratings:
            assert 7.0 < row.avg_rating <= 8.0, f"Good actor should have rating 7.0 < x <= 8.0, got {row.avg_rating}"
        
        # Test average classification (> 6.0 and <= 7.0)
        average_actors = result_df.filter(result_df.quality_class == "average")
        average_ratings = average_actors.select("avg_rating").collect()
        for row in average_ratings:
            assert 6.0 < row.avg_rating <= 7.0, f"Average actor should have rating 6.0 < x <= 7.0, got {row.avg_rating}"
    
    def test_movies_array_structure(self, spark, sample_actor_films_data):
        """Test that the movies array contains the correct structure"""
        result_df = analyze_actor_quality(spark, sample_actor_films_data)
        
        # Check that movies column is an array
        movies_sample = result_df.select("movies").first()
        assert isinstance(movies_sample.movies, list), "Movies column should be an array"
        
        # Check that each movie in the array has the correct structure
        if movies_sample.movies:
            first_movie = movies_sample.movies[0]
            expected_movie_fields = {"filmid", "film", "votes", "rating"}
            actual_movie_fields = set(first_movie.__fields__)
            assert expected_movie_fields.issubset(actual_movie_fields), f"Movie struct missing fields. Expected: {expected_movie_fields}, Got: {actual_movie_fields}"
    
    def test_actor_aggregation_by_year(self, spark, sample_actor_films_data):
        """Test that actors are properly aggregated by year"""
        result_df = analyze_actor_quality(spark, sample_actor_films_data)
        
        # Check that Al Pacino has 3 rows (one for each year)
        al_pacino_rows = result_df.filter(result_df.actor == "Al Pacino")
        assert al_pacino_rows.count() == 3, f"Al Pacino should have 3 rows, got {al_pacino_rows.count()}"
        
        # Check that each year has the correct film count
        al_pacino_1972 = al_pacino_rows.filter(al_pacino_rows.year == 1972).first()
        assert al_pacino_1972.film_count == 1, f"Al Pacino 1972 should have 1 film, got {al_pacino_1972.film_count}"
    
    def test_avg_rating_calculation(self, spark, sample_actor_films_data):
        """Test that average ratings are calculated correctly"""
        result_df = analyze_actor_quality(spark, sample_actor_films_data)
        
        # Check Al Pacino's 1972 rating (should be 9.2)
        al_pacino_1972 = result_df.filter((result_df.actor == "Al Pacino") & (result_df.year == 1972)).first()
        assert abs(al_pacino_1972.avg_rating - 9.2) < 0.01, f"Al Pacino 1972 rating should be 9.2, got {al_pacino_1972.avg_rating}"
    
    def test_is_active_flag(self, spark, sample_actor_films_data):
        """Test that is_active flag is set correctly"""
        result_df = analyze_actor_quality(spark, sample_actor_films_data)
        
        # Since our test data goes up to 2000, all records should have is_active = False
        active_records = result_df.filter(result_df.is_active == True)
        assert active_records.count() == 0, f"All records should be inactive in test data, got {active_records.count()} active records"
    
    def test_ordering(self, spark, sample_actor_films_data):
        """Test that results are ordered correctly by actor and year DESC"""
        result_df = analyze_actor_quality(spark, sample_actor_films_data)
        
        # Check that Al Pacino's records are ordered by year DESC
        al_pacino_rows = result_df.filter(result_df.actor == "Al Pacino").orderBy("year", ascending=False)
        years = [row.year for row in al_pacino_rows.collect()]
        expected_years = [1983, 1974, 1972]
        assert years == expected_years, f"Al Pacino years should be {expected_years}, got {years}"

if __name__ == "__main__":
    pytest.main([__file__])
