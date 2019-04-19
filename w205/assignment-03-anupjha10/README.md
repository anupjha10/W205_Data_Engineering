# template-activity-03


# Query Project

- In the Query Project, you will get practice with SQL while learning about
  Google Cloud Platform (GCP) and BiqQuery. You'll answer business-driven
  questions using public datasets housed in GCP. To give you experience with
  different ways to use those datasets, you will use the web UI (BiqQuery) and
  the command-line tools, and work with them in jupyter notebooks.

- We will be using the Bay Area Bike Share Trips Data
  (https://cloud.google.com/bigquery/public-data/bay-bike-share). 

#### Problem Statement
- You're a data scientist at Ford GoBike (https://www.fordgobike.com/), the
  company running Bay Area Bikeshare. You are trying to increase ridership, and
  you want to offer deals through the mobile app to do so. What deals do you
  offer though? Currently, your company has three options: a flat price for a
  single one-way trip, a day pass that allows unlimited 30-minute rides for 24
  hours and an annual membership. 

- Through this project, you will answer these questions: 
  * What are the 5 most popular trips that you would call "commuter trips"?
  * What are your recommendations for offers (justify based on your findings)?


## Assignment 03 - Querying data from the BigQuery CLI - set up 

### What is Google Cloud SDK?
- Read: https://cloud.google.com/sdk/docs/overview

- If you want to go further, https://cloud.google.com/sdk/docs/concepts has
  lots of good stuff.

### Get Going

- Install Google Cloud SDK: https://cloud.google.com/sdk/docs/

- Try BQ from the command line:

  * General query structure

    ```
    bq query --use_legacy_sql=false '
        SELECT count(*)
        FROM
           `bigquery-public-data.san_francisco.bikeshare_trips`'
    ```

### Queries

1. Rerun last week's queries using bq command line tool (Paste your bq
   queries):

- What's the size of this dataset? (i.e., how many trips)  
Answer: To find the total number of trips we would run the count SQL. The SQL using bq CLI would be
```
bq query --use_legacy_sql=false 'SELECT count(*) as number_of_trips 
                                  FROM `bigquery-public-data.san_francisco.bikeshare_trips`'
```	
The output of the above SQL is  

```	
+-----------------+
| number_of_trips |
+-----------------+
|          983648 |
+-----------------+
```	
So the answer is **983648**  

- What is the earliest start time and latest end time for a trip?  
Answer: To find the earliest start time and latest end time we would need to get the time component from the start date and the end date and get the minimum and maximum of those respectively. The SQL using bq CLI would be:  
```
bq query --use_legacy_sql=false 'SELECT min(time(start_date)) as earliest_start_time,max(time(end_date)) as latest_end_time
                                  FROM `bigquery-public-data.san_francisco.bikeshare_trips`'
```
The output of the query is :  
```
+---------------------+-----------------+
| earliest_start_time | latest_end_time |
+---------------------+-----------------+
|            00:00:00 |        23:59:00 |
+---------------------+-----------------+
```
So the earliest time of a trip is **00:00:00** and latest end time for a trip is **23:59:00**  

- How many bikes are there?  
Answer: To find the total number of bikes we need to count the distinct **bike_number**  
The sql query using bq CLI would be :  
```
bq query --use_legacy_sql=false 'SELECT count(distinct bike_number) as total_no_of_bikes 
                                   FROM `bigquery-public-data.san_francisco.bikeshare_trips`'
```
The output of the query is:  
```
+-------------------+
| total_no_of_bikes |
+-------------------+
|               700 |
+-------------------+
```
So the answer is **700**  

2. New Query (Paste your SQL query and answer the question in a sentence):

- How many trips are in the morning vs in the afternoon?  
Answer: To figure out how many trips are there in morning vs how many are in the afternoon we first need to define what we call as morning and what we define as afternoon. I am assuming morning means between 6:00AM to 10:00AM while afternoon means between 12:00 Noon to 3:00PM . And I am also using the start_date for figuring out if the trip is in morning or afternoon. It doesn't matter when did the trip end. Now, To construct the SQL query we would write conditional expression to return 1 or 0 if the start_date falls in morning and similarly second column of the query for afternoon.Then we would sum the return from the conditional expression.   
The SQL using bq CLI would be :
```
bq query --use_legacy_sql=false ' SELECT 
                                  SUM(IF(EXTRACT(HOUR FROM start_date)BETWEEN 6 AND 10,1,0)
                                      ) number_of_morning_trips,
                                  SUM(IF(EXTRACT(HOUR FROM start_date)BETWEEN 12 AND 15,1,0)
                                      ) number_of_afternoon_trips  
                                    FROM `bigquery-public-data.san_francisco.bikeshare_trips`'
```
The output of the query is :  
```
+-------------------------+---------------------------+
| number_of_morning_trips | number_of_afternoon_trips |
+-------------------------+---------------------------+
|                  359414 |                    176142 |
+-------------------------+---------------------------+
```

So the answer is total number of morning trips is **359414** and number of afternoon trips is **176142**. So Bike trips are more popular in morning.  
### Project Questions
Identify the main questions you'll need to answer to make recommendations (list
below, add as many questions as you need).

- Question 1: How do we define commuter trip and how many commuter trips are there in the dataset
 
- Question 2: For the commuter trips how many trips are bewteen duration of 30 mins to 45 mins 

- Question 3: For the commuter trips how many trips are bewteen duration of 15 mins to 30 mins

- Question 4: For non commuter trips which 5 station combinations are the least popular

- Question 5: Which 20 zip codes of the customer's are the least popular

- Question 6: For the commuter trips how many customer's are yearly or monthly subscriber and how many are short term customers

- Question 7: For non commuter trips which 5 station combinations are the most popular

- Question 8: Which are the top 10 stations which have the highest average trips starting in the morining

- Question 9: Which are the top 10 stations which have the highest average trips starting in the afternoon

- Question 10: Which are the Top 10 stations which have the average hourly number of trips starting close to the capacity of the station

 
- ...

- Question n: 

### Answers

Answer at least 4 of the questions you identified above You can use either
BigQuery or the bq command line tool.  Paste your questions, queries and
answers below.

- Question 1: How do we define commuter trip and how many commuter trips are there in the dataset   
  * Answer: We can define commuter trip as a trip which has different start station and end station. Which would mean the bike was used to go from one place to the other such as from home to work rather than used by tourist who will generally drop the bike on the same station from where she/he rented the bike. To get the number of such trips we can run the count with the where clause where the start_station_name != end_station_name.  
  * SQL query using bq CLI would be:     
```
bq query --use_legacy_sql=false ' 
             SELECT count(*) as Number_of_commuter_trips
               FROM `bigquery-public-data.san_francisco.bikeshare_trips`
	          WHERE start_station_name != end_station_name'
```
Output of the query is:  
```
+--------------------------+
| Number_of_commuter_trips |
+--------------------------+
|                   951601 |
+--------------------------+
```

So we see that total number of commuter trips is **951601** .So most of the trips are actually commuter trips.
 

- Question 2: For the commuter trips how many trips are bewteen duration of 30 mins to 45 mins
  * Answer: To find this we would run the count sql for commuter trips with additional where condition on duration_sec >=1800 and duration_sec <2700
  * SQL query using bq CLI would be:     
```
bq query --use_legacy_sql=false ' 
             SELECT count(*) as Number_of_commuter_trips_between_30_45_mins
               FROM `bigquery-public-data.san_francisco.bikeshare_trips`
	          WHERE start_station_name != end_station_name
			   AND duration_sec >=1800
			   AND duration_sec < 2700'
```
Output of the query is:  
```
+---------------------------------------------+
| Number_of_commuter_trips_between_30_45_mins |
+---------------------------------------------+
|                                       10325 |
+---------------------------------------------+
```
So the answer is **10325**


- Question 3: For the commuter trips how many trips are bewteen duration of 15 mins to 30 mins  
  * Answer: To find this we would run the count sql for commuter trips with additional where condition on duration_sec >=900 and duration_sec <1800
  * SQL query using bq CLI would be:   
```
bq query --use_legacy_sql=false ' 
             SELECT count(*) as Number_of_commuter_trips_between_15_30_mins
               FROM `bigquery-public-data.san_francisco.bikeshare_trips`
	          WHERE start_station_name != end_station_name
			   AND duration_sec >=900
			   AND duration_sec < 1800'
```
Output of the query is:  
```
+---------------------------------------------+
| Number_of_commuter_trips_between_15_30_mins |
+---------------------------------------------+
|                                      103956 |
+---------------------------------------------+
```
So the answer is **103956**  

- Question 4: For non commuter trips which 5 stations are the least popular  
  * Answer: To find this we would run the count sql with group by on start_station_name where start and end stations are the same. Then limit the output to 5 rows.  
  * SQL query using bq CLI would be:   
```
bq query --use_legacy_sql=false ' 
             SELECT start_station_name, count(*) as Number_of_non_commuter_trips
               FROM `bigquery-public-data.san_francisco.bikeshare_trips`
	          WHERE start_station_name = end_station_name
			  GROUP BY start_station_name
			  ORDER BY Number_of_non_commuter_trips
			  LIMIT 5'
```
Output of the query is:  
```
+-----------------------------+------------------------------+
|     start_station_name      | Number_of_non_commuter_trips |
+-----------------------------+------------------------------+
| 5th St at Folsom St         |                            2 |
| Sequoia Hospital            |                            4 |
| Kaiser Hospital             |                            6 |
| 5th S at E. San Salvador St |                            7 |
| Mezes                       |                           10 |
+-----------------------------+------------------------------+
```

So the answer is **5th St at Folsom St, Sequoia Hospital, Kaiser Hospital, 5th S at E. San Salvador St, Mezes**  

