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

## Spark fundementals

** This feedback is auto-generated from an LLM **

Dear Student,

Thank you for your submission of the PySpark assignment. I have reviewed your code and have the following feedback:

Disabling Automatic Broadcast Join:

You correctly disabled the default broadcast join behavior using spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1"). This is in line with the assignment requirement.
Explicitly Broadcasting Joins:

You properly used F.broadcast() to explicitly broadcast the medals and maps tables before joining them. This satisfies query_2. Note that the aliasing used is appropriate and enhances readability.
Bucket Join Strategy:

The task required using a bucket join strategy. However, your use of repartitionByRange(16, "match_id") does not implement bucket joins. Bucket joins require buckets to be specified during initial table creation or by using the bucketBy method during table writes. Merely repartitioning does not achieve this. Unfortunately, this does not meet the assignment criteria for query_3.
Aggregation Queries:

The aggregations for the questions appear almost correct:
Query 4a: You calculated the average kills per game per player, which seems theoretically correct. However, I would suggest verifying that you aren't computing averages twice unnecessarily (F.avg("kills") then F.avg("avg_kills")). Ensure performance and correctness checks.
Query 4b, 4c: You did well here by using count() and ordering by descending order which identifies the top records.
Query 4d: Filtering for "Killing Spree" is correct. Ensure you are filtering by the actual column medal_name.
Data Size Optimization:

You've applied sortWithinPartitions on most_played_playlist and most_played_map. While this is a good practice for performance optimization, you need to demonstrate partitioning strategies using fields like playlist or map_name for query_5. Explore using partitioning strategies on these low-cardinality fields instead of solely relying on repartitionByRange.
Output Display:

Your usage of .show() to display results remains satisfactory for demonstration purposes.
Overall, your submission demonstrates a solid understanding of broadcasting and aggregation; however, there was a misunderstanding in implementing bucket joins and data partitioning optimizations appropriately. Below is your final grade according to the evaluation rubric.

FINAL GRADE:

{
  "letter_grade": "B",
  "passes": true
}
Moving forward, I suggest reviewing the concept of bucket joins and partitioning strategies in Spark for improved performance and correctness. If you have any questions, feel free to reach out for clarification or further resources
