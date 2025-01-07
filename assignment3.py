from pyspark.sql import functions as F

# Disable automatic broadcast join to force explicit joins
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")

# Read the tables
medals_broadcast = F.broadcast(spark.read.table("medals").alias("medals"))
maps_broadcast = F.broadcast(spark.read.table("maps").alias("maps"))

match_details = spark.read.table("match_details")
matches = spark.read.table("matches")
medal_matches_players = spark.read.table("medal_matches_players")

# 2. **Join the Dataframes** with explicit broadcasts for small tables
joined_df = match_details \
    .join(matches, "match_id", "inner") \
    .join(medal_matches_players, "match_id", "inner") \
    .join(medals_broadcast, "medal_id", "inner") \
    .join(maps_broadcast, "map_id", "inner")

# 3. **Aggregations**

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

# 4. **Optimizing Data Processing**
# Partition the data based on low-cardinality fields to reduce shuffle
most_played_playlist = most_played_playlist.repartition(4, "playlist")
most_played_map = most_played_map.repartition(4, "map_name")

# 5. **Sort within partitions** to optimize the query performance further
sorted_by_playlist = most_played_playlist.sortWithinPartitions("playlist")
sorted_by_map = most_played_map.sortWithinPartitions("map_name")

# Show the results
most_kills.show()
most_played_playlist.show()
most_played_map.show()
most_killing_spree_map.show()
sorted_by_playlist.show()
sorted_by_map.show()
