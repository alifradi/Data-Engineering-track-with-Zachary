# Assignment 8: Tableau Dashboard Creation Guide

## 📊 **Assignment Overview**
Create two dashboards with Tableau Public using gaming data:
1. **Executive Dashboard** - High-level metrics for stakeholders
2. **Exploratory Dashboard** - Interactive analysis with filters

## 🎮 **Data Structure (UPDATED - Fixed Data Relationships)**

### **Data Files Available:**
- **`medals.csv`** - Medal types and point values
- **`matches.csv`** - Match information (maps, playlists, winners, duration)
- **`match_details.csv`** - Player performance in each match
- **`medals_matches_players.csv`** - Medal achievements by players (FIXED relationships)

### **Key Data Relationships (Now Consistent!):**
- **Each match has exactly 10 players** (from `match_details`)
- **Each match awards exactly 5 medals** (from `medals_matches_players`)
- **Player IDs are consistent** between performance and medal data
- **No more data inflation** - clean, meaningful relationships

### **Sample Data Values:**
- **Match Duration**: 1200-2100 seconds (20-35 minutes)
- **Player Performance**: 0-19 kills, 0-24 assists per match
- **Medal Points**: 25-300 points per medal type
- **Maps**: Summoner's Rift, Howling Abyss, Twisted Treeline
- **Playlists**: Ranked Solo, Ranked Flex, Normal Draft, Normal Blind, ARAM

## 🏆 **Executive Dashboard Creation**

### **Step 1: Create KPIs Sheet**
1. **New Sheet** → Name: "KPIs"
2. **Add Measures**:
   - **Total Matches**: `COUNTD(match_id)` from `matches.csv`
   - **Total Players**: `COUNTD(player_id)` from `match_details.csv`
   - **Average Match Duration**: `AVG(match_duration)/60` from `matches.csv`
3. **Format**: Large numbers, clear labels

### **Step 2: Create Map Popularity Chart**
1. **New Sheet** → Name: "Matches by Map"
2. **Columns**: `map_name` (from `matches.csv`)
3. **Rows**: `COUNT(match_id)` (from `matches.csv`)
4. **Chart Type**: Horizontal Bar Chart
5. **Title**: "Matches Played by Map"

### **Step 3: Create Win Distribution Chart**
1. **New Sheet** → Name: "Win Distribution"
2. **Columns**: `winner` (from `matches.csv`)
3. **Rows**: `COUNT(match_id)` (from `matches.csv`)
4. **Chart Type**: Pie Chart
5. **Title**: "Win Distribution by Team"

### **Step 4: Create Top Players Chart**
1. **New Sheet** → Name: "Top Players by Kills"
2. **Columns**: `SUM(kills)` (from `match_details.csv`)
3. **Rows**: `player_name` (from `match_details.csv`)
4. **Chart Type**: Horizontal Bar Chart
5. **Filter**: Top 5 players
6. **Title**: "Top 5 Players by Total Kills"

### **Step 5: Create MVP Chart**
1. **New Sheet** → Name: "Most Valuable Players"
2. **Columns**: `SUM(points)` (from `medals.csv` joined with `medals_matches_players.csv`)
3. **Rows**: `player_name` (from `match_details.csv`)
4. **Chart Type**: Horizontal Bar Chart
5. **Filter**: Top 5 players
6. **Title**: "Top 5 MVP Players by Medal Points"

### **Step 6: Create Team Players Chart**
1. **New Sheet** → Name: "Best Team Players"
2. **Columns**: `SUM(assists)` (from `match_details.csv`)
3. **Rows**: `player_name` (from `match_details.csv`)
4. **Chart Type**: Horizontal Bar Chart
5. **Filter**: Top 5 players
6. **Title**: "Top 5 Team Players by Total Assists"

### **Step 7: Create Medal Distribution Chart**
1. **New Sheet** → Name: "Medal Distribution"
2. **Columns**: `SUM(points)` (from `medals.csv`)
3. **Rows**: `medal_name` (from `medals.csv`)
4. **Chart Type**: Horizontal Bar Chart
5. **Title**: "Medal Distribution by Points Value"

### **Step 8: Combine into Executive Dashboard**
1. **New Dashboard** → Name: "Executive Dashboard - Gaming Analytics"
2. **Arrange Charts**:
   - **Top Row**: KPIs + Map Popularity
   - **Middle Row**: Win Distribution + Top Players by Kills
   - **Bottom Row**: MVP Players + Best Team Players + Medal Distribution

## 🔍 **Exploratory Dashboard Creation**

### **Step 1: Create Player Performance Analysis**
1. **New Sheet** → Name: "Player Performance"
2. **Columns**: `player_name` (from `match_details.csv`)
3. **Rows**: `SUM(kills)` (from `match_details.csv`)
4. **Chart Type**: Horizontal Bar Chart
5. **Add Filter**: `player_name` (interactive filter)
6. **Title**: "Player Performance by Kills"

### **Step 2: Create Map Analysis**
1. **New Sheet** → Name: "Map Analysis"
2. **Columns**: `map_name` (from `matches.csv`)
3. **Rows**: `COUNT(match_id)` (from `matches.csv`)
4. **Chart Type**: Horizontal Bar Chart
5. **Add Filter**: `map_name` (interactive filter)
6. **Title**: "Match Count by Map"

### **Step 3: Create Medal Analysis**
1. **New Sheet** → Name: "Medal Analysis"
2. **Columns**: `SUM(points)` (from `medals.csv`)
3. **Rows**: `medal_name` (from `medals.csv`)
4. **Chart Type**: Horizontal Bar Chart
5. **Add Filter**: `medal_name` (interactive filter)
6. **Title**: "Medal Points by Type"

### **Step 4: Create Performance Comparison**
1. **New Sheet** → Name: "Performance Comparison"
2. **Columns**: `SUM(kills)` (from `match_details.csv`)
3. **Rows**: `SUM(assists)` (from `match_details.csv`)
4. **Chart Type**: Scatter Plot
5. **Add Filter**: `player_name` (interactive filter)
6. **Title**: "Kills vs Assists Performance"

### **Step 5: Combine into Exploratory Dashboard**
1. **New Dashboard** → Name: "Exploratory Dashboard - Gaming Analytics"
2. **Arrange Charts**:
   - **Top Row**: Player Performance + Map Analysis
   - **Bottom Row**: Medal Analysis + Performance Comparison
3. **Add All Filters** to the right side for easy access

## 🔗 **Data Relationships in Tableau**

### **Primary Relationships:**
1. **`matches.csv` ↔ `match_details.csv`**: Join on `match_id`
2. **`matches.csv` ↔ `medals_matches_players.csv`**: Join on `match_id`
3. **`medals.csv` ↔ `medals_matches_players.csv`**: Join on `medal_id`
4. **`match_details.csv` ↔ `medals_matches_players.csv`**: Join on `match_id` AND `player_id`

### **Why This Works Now:**
- **Player IDs are consistent** across all tables
- **No more many-to-many join issues**
- **Clean, meaningful relationships** between performance and achievements

## 📊 **Dashboard Features to Highlight**

### **Executive Dashboard:**
- **KPIs**: Overall game statistics
- **Map Popularity**: Most played maps
- **Win Distribution**: Team performance
- **Player Rankings**: Top performers in different categories
- **Medal System**: Achievement structure

### **Exploratory Dashboard:**
- **Interactive Filters**: Player, map, medal selection
- **Performance Analysis**: Individual player insights
- **Comparative Views**: Kills vs assists, map preferences
- **Medal Tracking**: Achievement patterns

## 🚀 **Publishing to Tableau Public**

### **Step 1: Executive Dashboard**
1. **File** → **Public** → **Save to Tableau Public As...**
2. **Name**: "Executive Dashboard - Gaming Analytics"
3. **Copy the URL** (should start with `https://public.tableau.com/views/...`)

### **Step 2: Exploratory Dashboard**
1. **File** → **Public** → **Save to Tableau Public As...**
2. **Name**: "Exploratory Dashboard - Gaming Analytics"
3. **Copy the URL** (should start with `https://public.tableau.com/views/...`)

## ✅ **Quality Checklist**

- [ ] Both dashboards created with all required charts
- [ ] Interactive filters working in Exploratory Dashboard
- [ ] Data relationships properly established
- [ ] Charts show meaningful insights (not inflated data)
- [ ] Both dashboards published to Tableau Public
- [ ] URLs accessible without login requirements

## 🎯 **Expected Results**

With the fixed data, you should see:
- **Clean relationships** between player performance and medals
- **Meaningful insights** in your charts
- **Professional-looking dashboards** ready for submission
- **No data inflation** or meaningless relationships

**Your dashboards will now demonstrate real data engineering skills with clean, consistent data!** 🎉
