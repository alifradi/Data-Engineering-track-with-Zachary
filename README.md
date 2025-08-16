# Data-Engineering-track-with-Zachary

## Dimensional data modeling

1- Use of CTEs (Common Table Expressions)  for temporaray table quering 

2- use of structs to compact data and create customized types

3- use of arrays to compact data

4- unnest of data for slice and dice operations

5- track changements and modeling for SCD (Slowly changing Dimensions)

6- incremental and one full methods for back filling tables

7- window functions for advanced data processing

8- creating graphs and advanced analytics (DDLs for vertices, edges and their use for analytics): check the memo

Review of the assignment:
 
Feedback on Dimensional Data Modeling Submission:

Data Definition Language (DDL):

The use of custom types like films and quality_class is a good approach to encapsulate information and manage enumerations, which makes your schema more expressive. However, it is worth noting that custom types might add complexity when altering schema data types or migrating databases in some systems.
The primary key definition for the actors table is well-thought-out. Combining actorid and year ensures unique entries each year per actor, which is crucial for accumulating historical data.
Cumulative Table Generation:

The use of common table expressions (CTEs) — years, actor_startings, actors_seasons, and movies_aggregated — is efficient for breaking down the query logic into manageable steps. This makes your SQL readable and modular, aiding in troubleshooting.
The logic used to categorize quality_class is straightforward and follows a simplistic tier system based on avg_rating. This is good, assuming ratings fall within expected ranges.
Actors History SCD Table:

Your DDL for the actors_history_scd table appropriately sets up the structure for type 2 slowly changing dimensions (SCD). Tracking is_active and quality_class aligns with good SCD principles.
Throughout the backfill query, the use of window functions (LAG) to identify changes in quality or activity status is apt and demonstrates an understanding of SQL analytics.
Backfill Query:

The query captures historical data changes well with streak identifiers and transition tracking, covering both the data integrity and iterative growth of states correctly.
The decision to cap the current_season at 2020 in the outcome is a good placeholder for further incremental steps.
Incremental Query for SCD:

The query effectively combines historical records with new data by using structures like unchanged_records, changed_records, and new_records, which is essential for maintaining accurate SCD.
The use of set operations (UNION ALL) ensures completeness, gathering from all necessary data streams into one output, indicating apt use of SQL in handling multi-source data aggregation.
General Constructive Feedback:

Consider including comments more thoroughly explaining each SQL section or step for enhanced clarity, especially beneficial for future maintainers or collaborators.
While the SQL logic is sound, incorporating indexed strategies could be considered in your design, depending on scale, to boost performance, especially for tables that grow significantly over time.
Final Evaluation:

Your submission demonstrates a comprehensive understanding of dimensional data modeling, especially in managing historical data changes with SCD. The provided queries are functional, with logical structuring and clear attempts at applying advanced SQL features (like window functions and CTEs) effectively.

FINAL GRADE:

{
  "letter_grade": "A",
  "passes": true
}

## Fact Data Modeling 


1- difference between Fact and dimensions tables

2- when a changing value is considered to belong to dimension or to fact table

3- transforming logging activities to fact table 

4- compacting logging history into binary rows for later easy advanced data analytics 

5- incremental data loading for logging activity

** This feedback is auto-generated from an LLM **

Hello! Here's my feedback on your submission for the Fact Data Modeling exercise:

De-duplication Query:

You attempted to remove duplicates from game_details using SQL's ROW_NUMBER(). However, both game_id and team_id are considered, but player_id has been omitted, which was part of the requirement.
The comment suggests comparing data size before and after deduplication, which is helpful for verification.
User Devices Activity Datelist DDL:

The table schema for user_devices_cumulated is close to what's needed, but there is a slight misalignment with the requirement. The device_activity_datelist should ideally look like a MAP<STRING, ARRAY[DATE]>, which can be better represented with browser types as keys and date arrays as values. Your current schema seems to focus on having DATE[].
User Devices Activity Datelist Implementation:

Your incremental query approach for populating user_devices_cumulated is organized and uses CTEs effectively.
The logic of coalescing between yesterday and today to append to device_activity_datelist is a valid approach for aggregation, though the date handling in coalesce might need careful adjustment for proper incrementation as + Interval '1 day' assumes continued daily processing.
The use of array_append maintains consistency of aggregated dates.
User Devices Activity Int Datelist:

The transformation of device_activity_datelist into datelist_int is correctly approached with cross joining and summing the results of powers of two, which respects the essence of base-2 transformation.
It is well-structured, though the final outcome might be overly specific in using bit(32), which potentially limits longer date aggregation if the intention is to cover a more extended timeline.
Host Activity Datelist DDL:

The schema outline is straightforward and aligns with requirements. Defining a primary key on host and date ensures unique record criteria.
General Feedback:

Consider refining the deduplication approach to encompass all required identifiers.
Ensure your schema captures the requirements of a MAP data structure for devices.
Readability is aided by consistent comments; keep this up.
Check alignment with data types that cater to broader use cases if required.
Your submission covered the five necessary queries effectively. While there are some areas for precision and improvement, your logical structuring and understanding of SQL are evident.

FINAL GRADE:

{
  "letter_grade": "B",
  "passes": true
}
Good work, and with slight adjustments, you'll be even stronger in these exercises. Let me know if there's anything unclear or if you need further feedback on this assignment!

## Spark fundementals and testing

### fundamentals

** This feedback is auto-generated from an LLM **

Hello,

Thank you for your submission of the Apache Spark Infrastructure homework assignment. I have reviewed your code, and here is my feedback on each component of the task:

Disabling Default Broadcast Joins

You have correctly disabled the automatic broadcast join setting with spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1"). Well done.
Explicitly Broadcast Join

You correctly broadcast the medals and maps tables using F.broadcast, which properly aligns with the task requirements.
Bucket Joins and Reading Bucketed Tables

It seems like your match_details, matches, and medals_matches_players tables are read as bucketed. However, it's not entirely clear how these tables were bucketed, as the creation of the bucket is assumed ("Read bucketed tables (assumes they were written with bucketBy match_id)"). It's essential to ensure these tables are bucketed by match_id with 16 buckets during their creation or writing as this affects join performance.
Aggregations (Queries 4a, 4b, 4c, 4d)

Query 4a: The calculation for "Which player has the highest average kills per game?" is correctly implemented using groupBy and agg operations to get the average kills.

Query 4b: The most played playlist is correctly obtained with a grouped and ordered DataFrame.

Query 4c: You performed the aggregation for the most played map correctly.

Query 4d: The query for the map with the most "Killing Spree" medals is correctly filtered and aggregated.

Optimization (Partitioning and Sorting)

You executed the partitioning strategies correctly, including repurposing with low and high cardinality fields and adding comments to clarify your intentions.

Applying sortWithinPartitions to ensure data is optimized for query performance was correctly implemented.

Improvements/Suggestions:

Provide more details on the preparation of your bucketed tables (e.g., code or steps) to ensure correctness in setting up the bucket-based join strategy.

You could also expand on how performance could be monitored to verify the impact of each partitioning and sorting strategy.

Overall, your submission covers all tasks appropriately with a good understanding of Spark operations, joins, aggregations, partitioning, and sorting strategies.

Here is your final grade based on the rubric:

{
  "letter_grade": "A",
  "passes": true
}



### Testing

** This feedback is auto-generated from an LLM **



Hello,

Thank you for submitting your assignment. I have reviewed your submission which involves converting PostgreSQL queries to SparkSQL, implementing PySpark jobs, and creating corresponding tests.

Here's the feedback for your submission:

### Conversion of PostgreSQL Queries to SparkSQL

1. **Device Activity Analysis:**
   - You successfully converted a PostgreSQL query into a SparkSQL query for analyzing device activity.
   - The logic for handling user device events, daily activity aggregation, and the final activity summary appears correct.
   - The usage of CTEs (`WITH` clauses) enhances readability.

2. **Actor Quality Analysis:**
   - The PostgreSQL-to-SparkSQL conversion for actor quality analysis is well implemented.
   - You've categorized actors into quality classes based on ratings and checked for active status correctly.

### PySpark Job Implementation

1. **Device Activity Analysis Job:**
   - The `analyze_device_activity` function is well-structured with appropriate use of DataFrame registration for SparkSQL execution.
   - The `generate_datelist_int` function correctly integrates binary computation for date list conversion.

2. **Actor Quality Analysis Job:**
   - The `analyze_actor_quality` function is effectively structured to perform aggregations and classifications based on ratings.

3. **Overall Code Quality:**
   - Best practices for Spark session management have been mostly followed, with `create_spark_session` encapsulating session creation logic.
   - The main functions are appropriately configured to allow testing and result showcasing.

### Tests

1. **Test Structure & Data Generation:**
   - You have used pytest fixtures to create a Spark session and generate sample data, which allows for clean and modular test design.
   - Test cases cover multiple aspects of the logic such as data structure validation, filtering, aggregation, classification, and ordering.

2. **Coverage & Assertions:**
   - Device activity tests verify the structure, filtering, aggregations, and ordered output appropriately.
   - Actor quality tests confirm the integrity of classifications and the correctness of computed averages and flags.

3. **Test Naming & Clarity:**
   - Test methods are well-named, indicative of the functionality being tested, leading to clear intentions.

Overall, the submission reflects a strong understanding of the task requirements and demonstrates adept application of PySpark for large scale data processing tasks.

### Areas for Improvement

- **Edge Cases:** Consider adding more edge case handling, such as scenarios where expected averages might be on boundary values or when activity lists are empty.
- **Code Documentation:** Additional inline comments can improve understanding of complex logic, especially around binary conversion logic in the date list generation.

### FINAL GRADE
```json
{
  "letter_grade": "A",
  "passes": true
}
```

Your work demonstrates a high level of proficiency and adherence to the assignment requirements. Keep up the good work! If you have any questions or need further clarification, feel free to reach out.

Best regards.

## 4-apache-flink-training
