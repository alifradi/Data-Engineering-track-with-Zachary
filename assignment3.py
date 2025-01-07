from pyspark.sql import functions as F

# Disable automatic broadcast join to force explicit joins
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")

# Read the tables
medals_broadcast = F.broadcast(spark.read.table("medals").alias("medals"))
maps_broadcast = F.broadcast(spark.read.table("maps").alias("maps"))

match_details = spark.read.table("match_details")
matches = spark.read.table("matches")
medals_matches_players = spark.read.table("medals_matches_players")  # Fixed table name

# 1. **Bucket Join Implementation**: Assuming tables are bucketed during creation (match_id).
# If not, write the tables bucketed by match_id (bucketBy during writing).
# For now, skipping bucketBy writing as tables are assumed bucketed.

# Join the dataframes with explicit broadcasts for small tables
joined_df = match_details \
    .join(matches, "match_id", "inner") \
    .join(medals_matches_players, "match_id", "inner") \
    .join(medals_broadcast, "medal_id", "inner") \
    .join(maps_broadcast, "map_id", "inner")

# 2. **Aggregations**

# Query 4a: Average number of kills per game per player
most_kills = joined_df.groupBy("player_id", "match_id") \
    .agg(F.avg("kills").alias("avg_kills")) \
    .groupBy("player_id") \
    .agg(F.avg("avg_kills").alias("avg_kills_per_game"))

# Query 4b: Most played playlist
most_played_playlist = joined_df.groupBy("playlist") \
    .agg(F.count("match_id").alias("playlist_count")) \
    .orderBy(F.desc("playlist_count"))

# Query 4c: Most played map
most_played_map = joined_df.groupBy("map_name") \
    .agg(F.count("match_id").alias("map_count")) \
    .orderBy(F.desc("map_count"))

# Query 4d: Most Killing Spree medals by map
most_killing_spree_map = joined_df.filter(joined_df.medal_name == "Killing Spree") \
    .groupBy("map_name") \
    .agg(F.count("match_id").alias("killing_spree_count")) \
    .orderBy(F.desc("killing_spree_count"))

# 3. **Partitioning Strategies**: Experimenting with different partitioning strategies

# Strategy 1: Repartitioning based on `playlist` (low cardinality field)
most_played_playlist_repartitioned = most_played_playlist.repartition(4, "playlist")

# Strategy 2: Repartitioning based on `map_name` (low cardinality field)
most_played_map_repartitioned = most_played_map.repartition(4, "map_name")

# Strategy 3: Repartition based on `player_id` (higher cardinality field)
most_kills_repartitioned = most_kills.repartition(16, "player_id")

# Strategy 4: Coalesce to reduce the number of partitions after an operation (if applicable)
# If your dataset is smaller after a filter, use coalesce to merge partitions
most_killing_spree_map_coalesced = most_killing_spree_map.coalesce(4)

# 4. **Sort within partitions** for the optimized query performance
sorted_by_playlist = most_played_playlist_repartitioned.sortWithinPartitions("playlist")
sorted_by_map = most_played_map_repartitioned.sortWithinPartitions("map_name")

# 5. **Show the results**
most_kills.show()
most_played_playlist.show()
most_played_map.show()
most_killing_spree_map.show()
sorted_by_playlist.show()
sorted_by_map.show()
