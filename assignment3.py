from pyspark.sql import functions as F

# Disable automatic broadcast join to force explicit joins
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")

# Read the tables (assuming tables are bucketed during table creation or writing)
medals_broadcast = F.broadcast(spark.read.table("medals").alias("medals"))
maps_broadcast = F.broadcast(spark.read.table("maps").alias("maps"))

# Read bucketed tables (assumes they were written with bucketBy match_id)
match_details = spark.read.table("bucketed_match_details")
matches = spark.read.table("bucketed_matches")
medals_matches_players = spark.read.table("bucketed_medals_matches_players")

# 1. **Join the dataframes with explicit broadcasts for small tables**
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

# Get the player with the highest average kills
most_kills_top_player = most_kills.orderBy(F.desc("avg_kills_per_game")).limit(1)

# Query 4b: Most played playlist
most_played_playlist = joined_df.groupBy("playlist") \
    .agg(F.count("match_id").alias("playlist_count")) \
    .orderBy(F.desc("playlist_count"))

# Get the top playlist
most_played_playlist_top = most_played_playlist.limit(1)

# Query 4c: Most played map
most_played_map = joined_df.groupBy("map_name") \
    .agg(F.count("match_id").alias("map_count")) \
    .orderBy(F.desc("map_count"))

# Get the top map
most_played_map_top = most_played_map.limit(1)

# Query 4d: Most Killing Spree medals by map
most_killing_spree_map = joined_df.filter(joined_df.medal_name == "Killing Spree") \
    .groupBy("map_name") \
    .agg(F.count("match_id").alias("killing_spree_count")) \
    .orderBy(F.desc("killing_spree_count"))

# Get the top map with the most Killing Spree medals
most_killing_spree_map_top = most_killing_spree_map.limit(1)

# 3. **Show the results**
most_kills_top_player.show()
most_played_playlist_top.show()
most_played_map_top.show()
most_killing_spree_map_top.show()
