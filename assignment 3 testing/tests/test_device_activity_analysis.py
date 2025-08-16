import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType, DateType, ArrayType
from src.jobs.device_activity_analysis import analyze_device_activity, generate_datelist_int

class TestDeviceActivityAnalysis:
    """Test class for device activity analysis functionality"""
    
    @pytest.fixture(scope="class")
    def spark(self):
        """Create a Spark session for testing"""
        spark = SparkSession.builder \
            .appName("TestDeviceActivityAnalysis") \
            .master("local[2]") \
            .config("spark.sql.adaptive.enabled", "false") \
            .getOrCreate()
        
        yield spark
        spark.stop()
    
    @pytest.fixture(scope="class")
    def sample_events_data(self, spark):
        """Create sample events data for testing"""
        schema = StructType([
            StructField("url", StringType(), True),
            StructField("referrer", StringType(), True),
            StructField("user_id", IntegerType(), True),
            StructField("device_id", IntegerType(), True),
            StructField("host", StringType(), True),
            StructField("event_time", TimestampType(), True)
        ])
        
        data = [
            ("/home", "google.com", 1001, 2001, "example.com", "2023-01-01 10:00:00"),
            ("/products", "google.com", 1001, 2001, "example.com", "2023-01-01 11:00:00"),
            ("/about", "bing.com", 1002, 2002, "example.com", "2023-01-01 12:00:00"),
            ("/contact", "direct", 1003, 2003, "example.com", "2023-01-01 13:00:00"),
            ("/home", "google.com", 1001, 2001, "example.com", "2023-01-02 09:00:00"),
            ("/products", "google.com", 1002, 2002, "example.com", "2023-01-02 10:00:00"),
            ("/about", "bing.com", 1003, 2003, "example.com", "2023-01-02 11:00:00"),
            ("/home", "google.com", 1001, 2001, "example.com", "2023-01-03 08:00:00"),
            ("/products", "direct", 1004, 2004, "example.com", "2023-01-03 09:00:00"),
            ("/about", "google.com", 1005, 2005, "example.com", "2023-01-03 10:00:00"),
            # Some events with null user_id to test filtering
            ("/home", "google.com", None, 2006, "example.com", "2023-01-01 14:00:00"),
            ("/products", "bing.com", None, 2007, "example.com", "2023-01-01 15:00:00")
        ]
        
        return spark.createDataFrame(data, schema)
    
    @pytest.fixture(scope="class")
    def sample_devices_data(self, spark):
        """Create sample devices data for testing"""
        schema = StructType([
            StructField("device_id", IntegerType(), True),
            StructField("browser_type", StringType(), True),
            StructField("device_type", StringType(), True),
            StructField("os_type", StringType(), True)
        ])
        
        data = [
            (2001, "Chrome", "Desktop", "Windows"),
            (2002, "Firefox", "Desktop", "MacOS"),
            (2003, "Safari", "Mobile", "iOS"),
            (2004, "Chrome", "Mobile", "Android"),
            (2005, "Edge", "Desktop", "Windows"),
            (2006, "Chrome", "Desktop", "Linux"),
            (2007, "Firefox", "Mobile", "Android")
        ]
        
        return spark.createDataFrame(data, schema)
    
    @pytest.fixture(scope="class")
    def expected_device_activity_data(self, spark):
        """Create expected output data for device activity analysis"""
        schema = StructType([
            StructField("user_id", IntegerType(), True),
            StructField("device_id", IntegerType(), True),
            StructField("browser_type", StringType(), True),
            StructField("active_days", IntegerType(), True),
            StructField("activity_dates", ArrayType(DateType()), True),
            StructField("total_events", IntegerType(), True),
            StructField("first_activity", DateType(), True),
            StructField("last_activity", DateType(), True)
        ])
        
        # Expected results based on the sample data
        data = [
            (1001, 2001, "Chrome", 3, ["2023-01-01", "2023-01-02", "2023-01-03"], 3, "2023-01-01", "2023-01-03"),
            (1002, 2002, "Firefox", 2, ["2023-01-01", "2023-01-02"], 2, "2023-01-01", "2023-01-02"),
            (1003, 2003, "Safari", 2, ["2023-01-01", "2023-01-02"], 2, "2023-01-01", "2023-01-02"),
            (1004, 2004, "Chrome", 1, ["2023-01-03"], 1, "2023-01-03", "2023-01-03"),
            (1005, 2005, "Edge", 1, ["2023-01-03"], 1, "2023-01-03", "2023-01-03")
        ]
        
        return spark.createDataFrame(data, schema)
    
    def test_analyze_device_activity_structure(self, spark, sample_events_data, sample_devices_data):
        """Test that the device activity analysis returns the correct structure"""
        result_df = analyze_device_activity(spark, sample_events_data, sample_devices_data)
        
        # Check that all expected columns are present
        expected_columns = {
            "user_id", "device_id", "browser_type", "active_days", 
            "activity_dates", "total_events", "first_activity", "last_activity"
        }
        actual_columns = set(result_df.columns)
        assert expected_columns.issubset(actual_columns), f"Missing columns. Expected: {expected_columns}, Got: {actual_columns}"
        
        # Check that we have the expected number of rows (5 users with valid data)
        assert result_df.count() == 5, f"Expected 5 rows, got {result_df.count()}"
    
    def test_user_device_activity_filtering(self, spark, sample_events_data, sample_devices_data):
        """Test that events with null user_id are properly filtered out"""
        result_df = analyze_device_activity(spark, sample_events_data, sample_devices_data)
        
        # Check that no null user_ids are in the result
        null_user_records = result_df.filter(result_df.user_id.isNull())
        assert null_user_records.count() == 0, "No records with null user_id should be present"
        
        # Check that we have the correct number of unique users
        unique_users = result_df.select("user_id").distinct()
        assert unique_users.count() == 5, f"Expected 5 unique users, got {unique_users.count()}"
    
    def test_activity_dates_aggregation(self, spark, sample_events_data, sample_devices_data):
        """Test that activity dates are properly aggregated"""
        result_df = analyze_device_activity(spark, sample_events_data, sample_devices_data)
        
        # Check user 1001 (Chrome) - should have 3 active days
        user_1001 = result_df.filter(result_df.user_id == 1001).first()
        assert user_1001.active_days == 3, f"User 1001 should have 3 active days, got {user_1001.active_days}"
        
        # Check that activity_dates is an array
        assert isinstance(user_1001.activity_dates, list), "activity_dates should be an array"
        assert len(user_1001.activity_dates) == 3, f"User 1001 should have 3 activity dates, got {len(user_1001.activity_dates)}"
    
    def test_total_events_calculation(self, spark, sample_events_data, sample_devices_data):
        """Test that total events are calculated correctly"""
        result_df = analyze_device_activity(spark, sample_events_data, sample_devices_data)
        
        # Check user 1001 - should have 3 total events
        user_1001 = result_df.filter(result_df.user_id == 1001).first()
        assert user_1001.total_events == 3, f"User 1001 should have 3 total events, got {user_1001.total_events}"
        
        # Check user 1004 - should have 1 total event
        user_1004 = result_df.filter(result_df.user_id == 1004).first()
        assert user_1004.total_events == 1, f"User 1004 should have 1 total event, got {user_1004.total_events}"
    
    def test_first_last_activity_dates(self, spark, sample_events_data, sample_devices_data):
        """Test that first and last activity dates are calculated correctly"""
        result_df = analyze_device_activity(spark, sample_events_data, sample_devices_data)
        
        # Check user 1001
        user_1001 = result_df.filter(result_df.user_id == 1001).first()
        assert str(user_1001.first_activity) == "2023-01-01", f"User 1001 first activity should be 2023-01-01, got {user_1001.first_activity}"
        assert str(user_1001.last_activity) == "2023-01-03", f"User 1001 last activity should be 2023-01-03, got {user_1001.last_activity}"
    
    def test_browser_type_join(self, spark, sample_events_data, sample_devices_data):
        """Test that browser_type is correctly joined from devices table"""
        result_df = analyze_device_activity(spark, sample_events_data, sample_devices_data)
        
        # Check that all browser types from devices are present
        browser_types = result_df.select("browser_type").distinct().collect()
        browser_type_values = [row.browser_type for row in browser_types]
        expected_browsers = ["Chrome", "Firefox", "Safari", "Edge"]
        
        for browser in expected_browsers:
            assert browser in browser_type_values, f"Browser type {browser} should be present in results"
    
    def test_ordering(self, spark, sample_events_data, sample_devices_data):
        """Test that results are ordered correctly by user_id, browser_type, active_days DESC"""
        result_df = analyze_device_activity(spark, sample_events_data, sample_devices_data)
        
        # Check that results are ordered by user_id first
        user_ids = [row.user_id for row in result_df.collect()]
        expected_user_order = [1001, 1002, 1003, 1004, 1005]
        assert user_ids == expected_user_order, f"User IDs should be ordered as {expected_user_order}, got {user_ids}"
    
    def test_datelist_int_generation_structure(self, spark, sample_events_data, sample_devices_data):
        """Test that datelist_int generation returns the correct structure"""
        device_activity_df = analyze_device_activity(spark, sample_events_data, sample_devices_data)
        result_df = generate_datelist_int(spark, device_activity_df)
        
        # Check that all expected columns are present
        expected_columns = {"user_id", "device_id", "browser_type", "activity_dates", "datelist_int"}
        actual_columns = set(result_df.columns)
        assert expected_columns.issubset(actual_columns), f"Missing columns. Expected: {expected_columns}, Got: {actual_columns}"
        
        # Check that we have the same number of rows
        assert result_df.count() == 5, f"Expected 5 rows, got {result_df.count()}"
    
    def test_datelist_int_calculation(self, spark, sample_events_data, sample_devices_data):
        """Test that datelist_int is calculated correctly"""
        device_activity_df = analyze_device_activity(spark, sample_events_data, sample_devices_data)
        result_df = generate_datelist_int(spark, device_activity_df)
        
        # Check that datelist_int is an integer
        user_1001 = result_df.filter(result_df.user_id == 1001).first()
        assert isinstance(user_1001.datelist_int, int), "datelist_int should be an integer"
        
        # Check that datelist_int is positive
        assert user_1001.datelist_int > 0, "datelist_int should be positive"
    
    def test_data_integrity(self, spark, sample_events_data, sample_devices_data):
        """Test that data integrity is maintained throughout the analysis"""
        device_activity_df = analyze_device_activity(spark, sample_events_data, sample_devices_data)
        datelist_int_df = generate_datelist_int(spark, device_activity_df)
        
        # Check that user counts remain the same
        device_activity_count = device_activity_df.select("user_id").distinct().count()
        datelist_int_count = datelist_int_df.select("user_id").distinct().count()
        
        assert device_activity_count == datelist_int_count, f"User count should remain the same. Device activity: {device_activity_count}, Datelist int: {datelist_int_count}"
        
        # Check that device_id and browser_type combinations remain the same
        device_activity_combos = device_activity_df.select("device_id", "browser_type").distinct().count()
        datelist_int_combos = datelist_int_df.select("device_id", "browser_type").distinct().count()
        
        assert device_activity_combos == datelist_int_combos, f"Device-browser combinations should remain the same. Device activity: {device_activity_combos}, Datelist int: {datelist_int_combos}"

if __name__ == "__main__":
    pytest.main([__file__])
