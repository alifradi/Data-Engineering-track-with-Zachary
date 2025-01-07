from pyspark.sql import functions as F

# Disable automatic broadcast join
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")

# Read the tables
medals_broadcast = F.broadcast(spark.read.table("medals").alias("medals"))
maps_broadcast = F.broadcast(spark.read.table("maps").alias("maps"))

match_details = spark.read.table("match_details")
matches = spark.read.table("matches")
medal_matches_players = spark.read.table("medal_matches_players")

# Repartition tables for bucket join
match_details = match_details.repartitionByRange(16, "match_id")
matches = matches.repartitionByRange(16, "match_id")
medal_matches_players = medal_matches_players.repartitionByRange(16, "match_id")

# Join the dataframes
joined_df = match_details \
    .join(matches, "match_id", "inner") \
    .join(medal_matches_players, "match_id", "inner") \
    .join(medals_broadcast, "medal_id", "inner") \
    .join(maps_broadcast, "map_id", "inner")

# Aggregations
most_kills = joined_df.groupBy("player_id", "match_id") \
    .agg(F.avg("kills").alias("avg_kills")) \
    .groupBy("player_id") \
    .agg(F.avg("avg_kills").alias("avg_kills_per_game"))

most_played_playlist = joined_df.groupBy("playlist") \
    .agg(F.count("match_id").alias("playlist_count")) \
    .orderBy(F.desc("playlist_count"))

most_played_map = joined_df.groupBy("map_name") \
    .agg(F.count("match_id").alias("map_count")) \
    .orderBy(F.desc("map_count"))

most_killing_spree_map = joined_df.filter(joined_df.medal_name == "Killing Spree") \
    .groupBy("map_name") \
    .agg(F.count("match_id").alias("killing_spree_count")) \
    .orderBy(F.desc("killing_spree_count"))

# Sorting within partitions
sorted_by_playlist = most_played_playlist.sortWithinPartitions("playlist")
sorted_by_map = most_played_map.sortWithinPartitions("map_name")

# Show the results
most_kills.show()
most_played_playlist.show()
most_played_map.show()
most_killing_spree_map.show()
sorted_by_playlist.show()
sorted_by_map.show()
