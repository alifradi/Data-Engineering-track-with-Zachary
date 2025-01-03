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


