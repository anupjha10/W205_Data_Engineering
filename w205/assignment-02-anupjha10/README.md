# Query Project
- In the Query Project, you will get practice with SQL while learning about Google Cloud Platform (GCP) and BiqQuery. You'll answer business-driven questions using public datasets housed in GCP. To give you experience with different ways to use those datasets, you will use the web UI (BiqQuery) and the command-line tools, and work with them in jupyter notebooks.
- We will be using the Bay Area Bike Share Trips Data (https://cloud.google.com/bigquery/public-data/bay-bike-share). 

#### Problem Statement
- You're a data scientist at Ford GoBike (https://www.fordgobike.com/), the company running Bay Area Bikeshare. You are trying to increase ridership, and you want to offer deals through the mobile app to do so. What deals do you offer though? Currently, your company has three options: a flat price for a single one-way trip, a day pass that allows unlimited 30-minute rides for 24 hours and an annual membership. 

- Through this project, you will answer these questions: 
  * What are the 5 most popular trips that you would call "commuter trips"?
  * What are your recommendations for offers (justify based on your findings)?


## Assignment 02: Querying Data with BigQuery

### What is Google Cloud?
- Read: https://cloud.google.com/docs/overview/

### Get Going

- Go to https://cloud.google.com/bigquery/
- Click on "Try it Free"
- It asks for credit card, but you get $300 free and it does not autorenew after the $300 credit is used, so go ahead (OR CHANGE THIS IF SOME SORT OF OTHER ACCESS INFO)
- Now you will see the console screen. This is where you can manage everything for GCP
- Go to the menus on the left and scroll down to BigQuery
- Now go to https://cloud.google.com/bigquery/public-data/bay-bike-share 
- Scroll down to "Go to Bay Area Bike Share Trips Dataset" (This will open a BQ working page.)


### Some initial queries
Paste your SQL query and answer the question in a sentence.

- What's the size of this dataset? (i.e., how many trips)  
 Answer:  To find the total number of trips we would run the count SQL.
  The SQL would be
  ```sql
    #standardSQL
     SELECT count(*) as number_of_trips
      FROM `bigquery-public-data.san_francisco.bikeshare_trips`  
  ```
  The output of the above SQL is  
  ```
   number_of_trips
   983648
  ```
  So the answer is **983648**  
- What is the earliest start time and latest end time for a trip?  
  Answer: To find the earliest start time and latest end time we would need to get the time component from the start date and the end date and get the minimum and maximum of those respectively. The SQL would be:  
```sql
#standardSQL
SELECT min(time(start_date)) as earliest_start_time,max(time(end_date)) as latest_end_time
  FROM `bigquery-public-data.san_francisco.bikeshare_trips` 
```
  The output of the query is :  
```
earliest_start_time	   latest_end_time
  00:00:00	              23:59:00
```

So the earliest time of a trip is **00:00:00** and latest end time for a trip is **23:59:00**  
- How many bikes are there?  
Answer: To find the total number of bikes we need to count the distinct **bike_number**  
The sql query would be :  
```sql
#standardSQL
SELECT count(distinct bike_number) as total_no_of_bikes
  FROM `bigquery-public-data.san_francisco.bikeshare_trips`  
```
The query output is:  
```
total_no_of_bikes
 700
```
So the answer is **700**  

### Questions of your own
- Make up 3 questions and answer them using the Bay Area Bike Share Trips Data.
- Use the SQL tutorial (https://www.w3schools.com/sql/default.asp) to help you with mechanics.

- Question 1: As part of the research question we would like to know which station combinations are the most popular among the bike riders ?  
   To get this answer we would run a sql query to get top 5 station combinations .  
  * Answer: The top 5 combinations of the stations are:  
```
start_station_name                         end_station_name
-----------------------------------        -----------------------------------                    
Harry Bridges Plaza (Ferry Building)       Embarcadero at Sansome              
San Francisco Caltrain 2 (330 Townsend)    Townsend at 7th                     
2nd at Townsend                            Harry Bridges Plaza (Ferry Building)
Harry Bridges Plaza (Ferry Building)       2nd at Townsend                     
Embarcadero at Sansome                     Steuart at Market                   

``` 
  * SQL query:
```sql
#standardSQL
SELECT  start_station_name,end_station_name,count(*) as number_of_trips
  FROM `bigquery-public-data.san_francisco.bikeshare_trips`
 GROUP BY start_station_name,end_station_name
ORDER BY number_of_trips DESC
LIMIT 5

```
The query output is :
```
start_station_name                         end_station_name                        number_of_trips
-------------------------------------     -------------------------------         ------------------
Harry Bridges Plaza (Ferry Building)       Embarcadero at Sansome                  9150
San Francisco Caltrain 2 (330 Townsend)    Townsend at 7th                         8508
2nd at Townsend                            Harry Bridges Plaza (Ferry Building)    7620
Harry Bridges Plaza (Ferry Building)       2nd at Townsend                         6888
Embarcadero at Sansome                     Steuart at Market                       6874
```

- Question 2: As a data scientist we would also like to know which month has the lowest ridership ?  
 To answer this question we will extract the month from the **start_date** and then take a count and get the month with least number of count.   

  * Answer: December Month has the lowest ridership. 
  * SQL query:  
```sql
#standardSQL
SELECT  extract(MONTH from start_date) as Ridership_month,count(*) number_of_rides
  FROM `bigquery-public-data.san_francisco.bikeshare_trips`  
 GROUP BY Ridership_month
 ORDER BY number_of_rides
 LIMIT 1
```
The output of the query is:  
```
Ridership_month	   number_of_rides
----------------   ---------------	 
12	            57961
```

- Question 3: We would also like to know which day of the week has the least ridership ?   
To answer this we would run the sql query to exract the DAYOFWEEK part from start date and gather the count and get the one with least count.Keeping in mind that when we extract DAYOFWEEK we get integer value between 1 and 7 where 1 means Sunday and 7 means Saturday. 
  * Answer: Sunday
  * SQL query:

```sql
#standardSQL
SELECT  extract(DAYOFWEEK from start_date) as Ridership_day,count(*) number_of_rides
  FROM `bigquery-public-data.san_francisco.bikeshare_trips`  
 GROUP BY Ridership_day
 ORDER BY number_of_rides
 LIMIT 1
```
The output of the query is :  
```
Ridership_day	number_of_rides	
--------------  --------------- 
1               51375	            
```


