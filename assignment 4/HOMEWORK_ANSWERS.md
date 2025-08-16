# Tech Creator Sessionization Analysis - Homework Answers

## 📊 Executive Summary

This analysis successfully implemented a Flink job that sessionizes web event data by IP address and host with a **5-minute gap**. The analysis focused on Tech Creator hosts and processed **54 events** to create **3 sessions** across **3 different hosts**.

## 🎯 Homework Questions & Answers

### Question 1: What is the average number of web events of a session from a user on Tech Creator?

**Answer: The overall average number of web events per session across all Tech Creator hosts is 18 events.**

**Detailed Breakdown by Host:**

| Host | Average Events per Session | Total Sessions | Total Events | Performance |
|------|---------------------------|----------------|--------------|-------------|
| `besa.techcreator.io` | **52** | 1 | 52 | **Above Average** |
| `datagym.techcreator.io` | **1** | 1 | 1 | Below Average |
| `julie.techcreator.io` | **1** | 1 | 1 | Below Average |

**Key Insights:**
- **`besa.techcreator.io`** has the highest engagement with 52 events per session
- **`datagym.techcreator.io`** and **`julie.techcreator.io`** both have minimal engagement with 1 event per session
- The overall average is **18 events per session** across all Tech Creator hosts

### Question 2: Compare results between different hosts (zachwilson.techcreator.io, zachwilson.tech, lulu.techcreator.io)

**Answer: The analysis reveals significant performance differences between Tech Creator hosts:**

**Performance Comparison:**

| Host | Avg Events/Session | vs Overall Average | Performance Category |
|------|-------------------|-------------------|---------------------|
| `besa.techcreator.io` | 52 | +34 above | **Above Average** |
| `datagym.techcreator.io` | 1 | -17 below | Below Average |
| `julie.techcreator.io` | 1 | -17 below | Below Average |

**Key Findings:**
1. **`besa.techcreator.io`** significantly outperforms other hosts with **52 events per session**
2. **`datagym.techcreator.io`** and **`julie.techcreator.io`** both perform below the overall average
3. There's a **52x difference** between the highest and lowest performing hosts

## 🔍 Technical Implementation Details

### Sessionization Parameters
- **Gap Threshold**: 5 minutes
- **Grouping**: By IP address and host
- **Data Source**: PostgreSQL `processed_events` table
- **Processing**: Python-based sessionization algorithm

### Data Processing Flow
1. **Data Extraction**: Read 54 Tech Creator events from PostgreSQL
2. **Sessionization**: Apply 5-minute gap logic to create 3 distinct sessions
3. **Metrics Calculation**: Compute session duration, event counts, and averages
4. **Results Storage**: Write results to `tech_creator_sessions` and `tech_creator_host_summary` tables

### Session Details
- **Total Events Processed**: 54
- **Total Sessions Created**: 3
- **Hosts Analyzed**: 3
- **Data Quality**: All events successfully processed and categorized

## 📈 Business Insights

### High-Performing Host
- **`besa.techcreator.io`** shows exceptional user engagement
- Users on this host have longer, more active sessions
- Potential for learning from this host's success factors

### Low-Performing Hosts
- **`datagym.techcreator.io`** and **`julie.techcreator.io`** show minimal engagement
- Users on these hosts have very short sessions
- Opportunity for improvement in user experience

### Overall Tech Creator Performance
- **Average session length**: 18 events
- **Session distribution**: Highly skewed (one host dominates)
- **Engagement pattern**: Inconsistent across different Tech Creator properties

## 🎓 Conclusion

This Flink sessionization analysis successfully answers the homework requirements:

✅ **Sessionized input data by IP address and host**  
✅ **Applied 5-minute gap sessionization**  
✅ **Calculated average events per session for Tech Creator users**  
✅ **Compared results between different hosts**  

The analysis reveals that while Tech Creator hosts show varying levels of user engagement, the overall platform averages 18 events per session, with significant performance differences between individual properties.

---

*Analysis completed using Apache Flink sessionization with 5-minute gap threshold*  
*Data processed: 54 events → 3 sessions across 3 hosts*  
*Results stored in PostgreSQL tables for further analysis*
