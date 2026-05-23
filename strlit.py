import streamlit as st
import pandas as pd
from sqlalchemy import create_engine,text

@st.cache_resource
def get_mysql_engine():
    username = "root"          
    password = "password" 
    host = "localhost"         
    port = "3306"              
    database = "traffic_analysis"   
    
    return create_engine(f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}")

engine = get_mysql_engine()

#st.title("Traffic Crash Analysis")
st.markdown(
    "<h1 style='text-align: center;'>Traffic Crash Analysis</h1>", 
    unsafe_allow_html=True
)
st.subheader("based on the Chicago Traffic Crashes dataset (2020-2026)")

query_choice = st.selectbox("Select a query to view the results:", [
    "Top 5 most dangerous combinations of weather and crash type",
    "Top 10 streets with the highest number of injury crashes",
    "Percentage of crashes that resulted in injuries for each crash type",
    "The peak crash hour for each month",
    "Top 5 primary causes of crashes during night time",
    "Average number of injuries in daylight vs darkness conditions",
    "Traffic control device type that has the highest average injuries per crash",
    "Top 5 locations (latitude/longitude) with the highest crash frequency",
    "Top 5 streets with the highest injury rate",
    "The most common crash type for each year",
    "Day of the week with the highest average crashes per hour",
    "High-risk time slots",
    "Top 3 contributing causes for each crash type",
    "Year-over-year growth rate of crashes",
    "Hotspot zones"
    
])

if query_choice == "Top 5 most dangerous combinations of weather and crash type":
    st.title("Top 5 most dangerous combinations of weather and crash type")
    query1 = """SELECT 
        WEATHER_CONDITION,
        FIRST_CRASH_TYPE,
        COUNT(*) AS Total_crashes
    FROM 
        traffic_analysis
    GROUP BY 
        WEATHER_CONDITION, 
        FIRST_CRASH_TYPE
    ORDER BY 
        Total_crashes DESC LIMIT 5"""
    df1 = pd.read_sql_query(query1, con=engine)
    st.dataframe(df1, use_container_width=True)
    st.markdown("The table above shows the top 5 most dangerous combinations of weather conditions and crash types based on the total number of crashes. We can see that all the top 5 Weather conditions are Clear and the most dangerous combination of all is Clear sky and parked Motor Vehicle.")



if query_choice == "Top 10 streets with the highest number of injury crashes":
    st.title("Top 10 streets with the highest number of injury crashes")
    query2 = """SELECT
        STREET_NAME,
        COUNT(*) AS Injury_crash_count,
        SUM(INJURIES_TOTAL) AS Total_injuries
    FROM
        traffic_analysis
    WHERE
        CRASH_TYPE = 'INJURY AND / OR TOW DUE TO CRASH'
        AND INJURIES_TOTAL > 0
    GROUP BY
        STREET_NAME
    ORDER BY
        Injury_crash_count DESC
    LIMIT 10;"""
    df2 = pd.read_sql_query(query2, con=engine)
    st.dataframe(df2, use_container_width=True)
    st.markdown("The table above lists the top 10 streets with the highest number of injury crashes. It includes the total count of injury crashes and the total number of injuries for each street. We can see that the Western Ave street has the highest number of injury crash event and total injured people per crash.")


if query_choice == "Percentage of crashes that resulted in injuries for each crash type":
    st.title("Percentage of crashes that resulted in injuries for each crash type.")
    query3 = """SELECT
        FIRST_CRASH_TYPE,
        COUNT(*) AS Total_crashes,
        SUM(CASE WHEN INJURIES_TOTAL > 0 THEN 1 ELSE 0 END) AS Injury_crashes,
        ROUND(
            SUM(CASE WHEN INJURIES_TOTAL > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 4
        ) AS Injury_percentage
    FROM
        traffic_analysis
    GROUP BY
        FIRST_CRASH_TYPE
    ORDER BY
        Injury_percentage DESC;"""
    df3 = pd.read_sql_query(query3, con=engine)
    st.dataframe(df3, use_container_width=True)
    st.markdown("The table above shows the percentage of crashes that resulted in injuries for each crash type. It includes the total number of crashes, the count of injury crashes, and the injury percentage for each crash type. It is clear that the crash type 'Pedastrian' has the highest injury percentage.")


if query_choice == "The peak crash hour for each month":
    st.title(" The peak crash hour for each month")
    query4 = """SELECT 
        CRASH_MONTH,
        CRASH_HOUR AS Peak_crash_hour,
        Total_crashes
    FROM (
        SELECT 
            CRASH_MONTH,
            CRASH_HOUR,
            COUNT(*) AS Total_crashes,
            ROW_NUMBER() OVER (
                PARTITION BY CRASH_MONTH 
                ORDER BY COUNT(*) DESC
            ) AS rnk
        FROM 
            traffic_analysis
        GROUP BY 
            CRASH_MONTH,
            CRASH_HOUR
    ) ranked_table
    WHERE rnk = 1
    ORDER BY 
        CRASH_MONTH;"""
    df4 = pd.read_sql_query(query4, con=engine)
    st.dataframe(df4, use_container_width=True)
    st.markdown("The table above identifies the peak crash hour for each month based on the total number of crashes. It shows the month, the hour when the most crashes happened, and the total number of crashes during that hour. It can be noted that throughout the year, the peak crash hour is between 3pm and 6pm (Evening time).")

if query_choice == "Top 5 primary causes of crashes during night time":
    st.title("Top 5 primary causes of crashes during night time")
    query5 = """SELECT
        PRIM_CONTRIBUTORY_CAUSE,
        COUNT(*) AS Total_crashes,
        SUM(INJURIES_FATAL) AS Fatal_crashes
    FROM
        traffic_analysis
    WHERE
        CRASH_HOUR >= 18
    GROUP BY
        PRIM_CONTRIBUTORY_CAUSE
    ORDER BY
        Total_crashes DESC
    LIMIT 5;"""
    df5 = pd.read_sql_query(query5, con=engine)
    st.dataframe(df5, use_container_width=True)
    st.markdown("The table above shows the top 5 primary causes of crashes during night time. It includes the total number of crashes and the count of fatal crashes for each cause. It can be noted from the results that the highest amount of the crashes that happen at night are due to causes that are unable to determine. ")

if query_choice == "Average number of injuries in daylight vs darkness conditions":
    st.title("Average number of injuries in daylight vs darkness conditions")
    query6 = """SELECT
        LIGHTING_CONDITION,
        AVG(INJURIES_TOTAL) AS Average_number_of_injuries
    FROM
        traffic_analysis
    WHERE
        LIGHTING_CONDITION != 'UNKNOWN'
    GROUP BY
        LIGHTING_CONDITION
    ORDER BY
        Average_number_of_injuries DESC;"""
    df6 = pd.read_sql_query(query6, con=engine)
    st.dataframe(df6, use_container_width=True)
    st.markdown("The table above shows the average number of injuries for each lighting condition. It can be noted that the average number of injuries is higher in darker lighting conditions compared to Daylight which has the lowest average.")

if query_choice == "Traffic control device type that has the highest average injuries per crash":
    st.title("Traffic control device type that has the highest average injuries per crash")
    query7 = """SELECT
        TRAFFIC_CONTROL_DEVICE,
        COUNT(*) AS Total_crashes,
        SUM(INJURIES_TOTAL) AS Total_injuries,
        AVG(INJURIES_TOTAL) AS Average_injuries_per_crash
    FROM
        traffic_analysis
    WHERE
        TRAFFIC_CONTROL_DEVICE NOT IN ('UNKNOWN', 'OTHER')
    GROUP BY
        TRAFFIC_CONTROL_DEVICE
    ORDER BY
        Average_injuries_per_crash DESC;"""
    df7 = pd.read_sql_query(query7, con=engine)
    st.dataframe(df7, use_container_width=True)
    st.markdown("The table above identifies the traffic control device type that has the highest average injuries per crash. It includes the total number of crashes, total injuries, and the average injuries per crash for each traffic control device type. It is evident that the Bicycle crossing sign has the highest average injuried per crash.")

if query_choice == "Top 5 locations (latitude/longitude) with the highest crash frequency":
    st.title("Top 5 locations (latitude/longitude) with the highest crash frequency")
    query8 = """SELECT
        LATITUDE,
        LONGITUDE,
        COUNT(*) AS Crash_frequency
    FROM
        traffic_analysis
    WHERE
        LATITUDE  IS NOT NULL
        AND LONGITUDE IS NOT NULL
    GROUP BY
        LATITUDE,
        LONGITUDE
    ORDER BY
        Crash_frequency DESC
    LIMIT 5;"""
    df8 = pd.read_sql_query(query8, con=engine)
    st.dataframe(df8, use_container_width=True)
    st.markdown("The table above lists the top 5 locations (latitude and longitude) with the highest crash frequency. It includes the latitude, longitude, and the total number of crashes that occurred at each location. This information can help identify high-risk areas.")

if query_choice == "Top 5 streets with the highest injury rate":
    st.title("Top 5 streets with the highest injury rate")
    query9 = """SELECT
        STREET_NAME,
        COUNT(*) AS Total_crashes,
        SUM(INJURIES_TOTAL) AS Total_injuries,
        ROUND(SUM(INJURIES_TOTAL)*100.0 / COUNT(*), 4) AS Injury_rate
    FROM
        traffic_analysis
    GROUP BY
        STREET_NAME
    HAVING
        COUNT(*) > 100
    ORDER BY
        Injury_rate DESC
    LIMIT 5;"""
    df9 = pd.read_sql_query(query9, con=engine)
    st.dataframe(df9, use_container_width=True)
    st.markdown("The table above lists the top 5 streets with the highest injury rate. It includes the street name, total crashes, total injuries, and the injury rate for each street. It can be noted that the Marquette DR street has the highest injury rate of all.")

if query_choice == "The most common crash type for each year":
    st.title("The most common crash type for each year")
    query10 = """SELECT
        year,
        FIRST_CRASH_TYPE AS Most_common_crash_type,
        Total_crashes
    FROM (
        SELECT
            year,
            FIRST_CRASH_TYPE,
            COUNT(*) AS Total_crashes,
            RANK() OVER (
                PARTITION BY year
                ORDER BY COUNT(*) DESC
            ) AS rnk
        FROM
            traffic_analysis
        GROUP BY
            year, FIRST_CRASH_TYPE
    ) ranked
    WHERE rnk = 1
    ORDER BY
        year;"""
    df10 = pd.read_sql_query(query10, con=engine)
    st.dataframe(df10, use_container_width=True)
    st.markdown("The table above identifies the most common crash type for each year based on the total number of crashes. It shows the year, the most common crash type, and the total number of crashes for that type in each year. It is evident that the most common crash type for the years 2020 to 2025 are Parked motor vehicles.")


if query_choice == "Day of the week with the highest average crashes per hour":
    st.title("Day of the week with the highest average crashes per hour")
    query11 = """SELECT
        CRASH_DAY_OF_WEEK,
        CASE CRASH_DAY_OF_WEEK
            WHEN 1 THEN 'Sunday'
            WHEN 2 THEN 'Monday'
            WHEN 3 THEN 'Tuesday'
            WHEN 4 THEN 'Wednesday'
            WHEN 5 THEN 'Thursday'
            WHEN 6 THEN 'Friday'
            WHEN 7 THEN 'Saturday'
        END AS Day_name,
        ROUND(AVG(crashes_per_hour), 2) AS Average_crashes_per_hour
    FROM (
        SELECT
            CRASH_DAY_OF_WEEK,
            CRASH_HOUR,
            COUNT(*) AS crashes_per_hour
        FROM
            traffic_analysis
        GROUP BY
            CRASH_DAY_OF_WEEK, CRASH_HOUR
    ) hourly
    GROUP BY
        CRASH_DAY_OF_WEEK
    ORDER BY
        Average_crashes_per_hour DESC;"""
    df11 = pd.read_sql_query(query11, con=engine)
    st.dataframe(df11, use_container_width=True)
    st.markdown("The table above shows the day of the week with the highest average crashes per hour. This information shows that Friday has the highest average crashes per hour.")

if query_choice == "High-risk time slots":
    st.title(" High-risk time slots")
    query12 = """SELECT
        Time_bucket,
        Total_crashes,
        Injury_crashes
    FROM (
        SELECT
            CASE
                WHEN CRASH_HOUR BETWEEN  5 AND 11 THEN 'Morning   (5AM  - 12PM)'
                WHEN CRASH_HOUR BETWEEN 12 AND 16 THEN 'Afternoon (12PM - 5PM) '
                WHEN CRASH_HOUR BETWEEN 17 AND 20 THEN 'Evening   (5PM  - 9PM)'
                ELSE                                    'Night     (9PM - 5AM) '
            END AS Time_bucket,
            COUNT(*) AS Total_crashes,
            SUM(CASE WHEN CRASH_TYPE = 'INJURY AND / OR TOW DUE TO CRASH'
                    THEN 1 ELSE 0 END) AS Injury_crashes
        FROM
            traffic_analysis
        GROUP BY
            Time_bucket
    ) bucketed
    ORDER BY
        Injury_crashes DESC;"""
    df12 = pd.read_sql_query(query12, con=engine)
    st.dataframe(df12, use_container_width=True)
    st.markdown("The table above shows the high-risk time slots with the highest number of injury crashes. This information tells us that Afternoon has the highest number of crashes involving injuries")

if query_choice == "Top 3 contributing causes for each crash type":
    st.title("Top 3 contributing causes for each crash type")
    query13 = """SELECT
        FIRST_CRASH_TYPE,
        PRIM_CONTRIBUTORY_CAUSE,
        Total_crashes,
        rnk
    FROM (
        SELECT
            FIRST_CRASH_TYPE,
            PRIM_CONTRIBUTORY_CAUSE,
            COUNT(*) AS Total_crashes,
            ROW_NUMBER() OVER (
                PARTITION BY FIRST_CRASH_TYPE
                ORDER BY COUNT(*) DESC
            ) AS rnk
        FROM
            traffic_analysis
        WHERE
            PRIM_CONTRIBUTORY_CAUSE NOT IN ('UNABLE TO DETERMINE', 'NOT APPLICABLE')
        GROUP BY
            FIRST_CRASH_TYPE,
            PRIM_CONTRIBUTORY_CAUSE
    ) ranked
    WHERE rnk <= 3
    ORDER BY
        FIRST_CRASH_TYPE, rnk;"""
    df13 = pd.read_sql_query(query13, con=engine)
    st.dataframe(df13, use_container_width=True)
    st.markdown("The table above lists the top 3 contributing causes for each crash type. It includes the crash type, the primary contributory cause, the total number of crashes for that cause, and the rank. We can see that 'Failing to yeild right-of-way' is the most common cause for Angle crashes with a total of 22827 crashes.")

if query_choice == "Year-over-year growth rate of crashes":
    st.title("Year-over-year growth rate of crashes")
    query14 = """SELECT
        year,
        Total_crashes,
        Previous_year_crashes,
        ROUND(
            (Total_crashes - Previous_year_crashes) * 100.0 / Previous_year_crashes, 2
        ) AS Growth_rate_percent
    FROM (
        SELECT
            year,
            COUNT(*) AS Total_crashes,
            LAG(COUNT(*)) OVER (
                ORDER BY year
            ) AS Previous_year_crashes
        FROM
            traffic_analysis
        GROUP BY
            year
    ) yearly
    ORDER BY
        year;"""
    df14 = pd.read_sql_query(query14, con=engine)
    st.dataframe(df14, use_container_width=True)
    st.markdown("The table above shows the year-over-year growth rate of crashes. It includes the year, total crashes for that year, total crashes for the previous year, and the growth rate percentage. We can see that the growth rate is the highest in 2021 and the value keeps fluctuating over the next years.")

if query_choice == "Hotspot zones":
    st.title(" Hotspot zones")
    query15 = """SELECT
        ROUND(LATITUDE,  2) AS Latitude,
        ROUND(LONGITUDE, 2) AS Longitude,
        COUNT(*) AS Total_crashes
    FROM
        traffic_analysis
    WHERE
        LATITUDE IS NOT NULL
        AND LONGITUDE IS NOT NULL
    GROUP BY
        ROUND(LATITUDE,  2),
        ROUND(LONGITUDE, 2)
    ORDER BY
        Total_crashes DESC
    LIMIT 10;"""
    df15 = pd.read_sql_query(query15, con=engine)
    st.dataframe(df15, use_container_width=True)
    st.markdown("The table above shows the top 10 hotspot zones with the highest number of crashes. This information can help identify areas with high crash frequencies.")

