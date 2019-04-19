# Assignment 12

## Summary
 In this assignment I spun up a cluster with zookeeper,kafka,spark,cloudera(with hive) ,presto and mids container.  
 In this assignment I create Flask api which generates messages to Kafka .  
 Spark session reads messages from kafka and stores in HDFS.  
 Spark program also creates Hive table which is read using presto .  
 I also create streaming spark job which writes to HDFS every 10 seconds.  
# Tasks

 I ran the following steps and commands to achieve the results

## Create the docker compose yaml file and then spin up the cluster with zookeeper, kafka, mids , spark, presto  and cloudera(with hive) hadoop  container.
```
 vi docker-compose.yml
 docker-compose up -d
```

## The docker compose yml file created was the following

```
---
version: '2'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 32181
      ZOOKEEPER_TICK_TIME: 2000
    expose:
      - "2181"
      - "2888"
      - "32181"
      - "3888"
    extra_hosts:
      - "moby:127.0.0.1"

  kafka:
    image: confluentinc/cp-kafka:latest
    depends_on:
      - zookeeper
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:32181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    expose:
      - "9092"
      - "29092"
    extra_hosts:
      - "moby:127.0.0.1"

  cloudera:
    image: midsw205/hadoop:0.0.2
    hostname: cloudera
    expose:
      - "8020" # nn
      - "8888" # hue
      - "9083" # hive thrift
      - "10000" # hive jdbc
      - "50070" # nn http
    ports:
      - "8888:8888"
    extra_hosts:
      - "moby:127.0.0.1"

  spark:
    image: midsw205/spark-python:0.0.6
    stdin_open: true
    tty: true
    volumes:
      - ~/w205:/w205
    expose:
      - "8888"
    #ports:
    #  - "8888:8888"
    depends_on:
      - cloudera
    environment:
      HADOOP_NAMENODE: cloudera
      HIVE_THRIFTSERVER: cloudera:9083
    extra_hosts:
      - "moby:127.0.0.1"
    command: bash

  presto:
    image: midsw205/presto:0.0.1
    hostname: presto
    volumes:
      - ~/w205:/w205
    expose:
      - "8080"
    environment:
      HIVE_THRIFTSERVER: cloudera:9083
    extra_hosts:
      - "moby:127.0.0.1"

  mids:
    image: midsw205/base:0.1.9
    stdin_open: true
    tty: true
    volumes:
      - ~/w205:/w205
    expose:
      - "5000"
    ports:
      - "5000:5000"
    extra_hosts:
      - "moby:127.0.0.1"

    
```
## Create a kafka topic called events
 ```
 docker-compose exec kafka kafka-topics --create --topic events --partitions 1 --replication-factor 1 --if-not-exists --zookeeper zookeeper:32181
 ```

## Created game api with following code
```python
#!/usr/bin/env python
import json
from kafka import KafkaProducer
from flask import Flask, request

app = Flask(__name__)
producer = KafkaProducer(bootstrap_servers='kafka:29092')


def log_to_kafka(topic, event):
    event.update(request.headers)
    producer.send(topic, json.dumps(event).encode())


@app.route("/")
def default_response():
    default_event = {'event_type': 'default'}
    log_to_kafka('events', default_event)
    return "This is the default response!\n"


@app.route("/purchase_a_sword")
def purchase_a_sword():
    purchase_sword_event = {'event_type': 'purchase_sword'}
    log_to_kafka('events', purchase_sword_event)
    return "Sword Purchased!\n"

```
## Run the game api using python and flask . It generates the return output for default url and purchase sword. These functions also log to kafka json messages
```
 docker-compose exec mids env FLASK_APP=/w205/assignment-12-anupjha10/game_api.py flask run --host 0.0.0.0
```
## Use apache bench in the mids container to generate messages in topic in kafka by calling the flask game api using the http protocol 
```
docker-compose exec mids ab -n 10 -H "Host: user1.comcast.com" http://localhost:5000/

docker-compose exec mids ab -n 10 -H "Host: user1.comcast.com" http://localhost:5000/purchase_a_sword

docker-compose exec mids ab -n 10 -H "Host: user2.att.com" http://localhost:5000/

docker-compose exec mids ab -n 10 -H "Host: user2.att.com" http://localhost:5000/purchase_a_sword
``` 
## Use the following spark python code to write the events to HDFS 
```python
#!/usr/bin/env python
"""Extract events from kafka and write them to hdfs
"""
import json
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import udf


@udf('boolean')
def is_purchase(event_as_json):
    event = json.loads(event_as_json)
    if event['event_type'] == 'purchase_sword':
        return True
    return False


def main():
    """main
    """
    spark = SparkSession \
        .builder \
        .appName("ExtractEventsJob") \
        .getOrCreate()

    raw_events = spark \
        .read \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("subscribe", "events") \
        .option("startingOffsets", "earliest") \
        .option("endingOffsets", "latest") \
        .load()

    purchase_events = raw_events \
        .select(raw_events.value.cast('string').alias('raw'),
                raw_events.timestamp.cast('string')) \
        .filter(is_purchase('raw'))

    extracted_purchase_events = purchase_events \
        .rdd \
        .map(lambda r: Row(timestamp=r.timestamp, **json.loads(r.raw))) \
        .toDF()
    extracted_purchase_events.printSchema()
    extracted_purchase_events.show()

    extracted_purchase_events \
        .write \
        .mode('overwrite') \
        .parquet('/tmp/purchases')


if __name__ == "__main__":
    main()

```

## Run the following command to run the above spark job 
```
docker-compose exec spark spark-submit /w205/assignment-12-anupjha10/filtered_writes.py
```

## Run the following to check the HDFS 
```
docker-compose exec cloudera hadoop fs -ls /tmp/

docker-compose exec cloudera hadoop fs -ls /tmp/purchases/
```

## The output is 
```
science@w205s5-crook-4:~/w205/assignment-12-anupjha10$ docker-compose exec cloudera hadoop fs -ls /tmp/
Found 4 items
drwxrwxrwt   - mapred mapred              0 2016-04-06 02:26 /tmp/hadoop-yarn
drwx-wx-wx   - hive   supergroup          0 2019-04-16 08:23 /tmp/hive
drwxrwxrwt   - mapred hadoop              0 2016-04-06 02:28 /tmp/logs
drwxr-xr-x   - root   supergroup          0 2019-04-16 08:32 /tmp/purchases
science@w205s5-crook-4:~/w205/assignment-12-anupjha10$ docker-compose exec cloudera hadoop fs -ls /tmp/purchases/
Found 2 items
-rw-r--r--   1 root supergroup          0 2019-04-16 08:32 /tmp/purchases/_SUCCESS
-rw-r--r--   1 root supergroup       1645 2019-04-16 08:32 /tmp/purchases/part-00000-c511adb8-31d4-4fbc-a216-279831a08434-c000.snappy.parquet
science@w205s5-crook-4:~/w205/assignment-12-anupjha10$

```

## Create external table in HIVE 
## We use the spark job to read from kafka and then create the hive table by reading the in-memory dataframe in spark and writing it to HDFS using the create external table command 
## The spark python file is the following 
```python
#!/usr/bin/env python
"""Extract events from kafka and write them to hdfs
"""
import json
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import udf


@udf('boolean')
def is_purchase(event_as_json):
    event = json.loads(event_as_json)
    if event['event_type'] == 'purchase_sword':
        return True
    return False


def main():
    """main
    """
    spark = SparkSession \
        .builder \
        .appName("ExtractEventsJob") \
        .enableHiveSupport() \
        .getOrCreate()

    raw_events = spark \
        .read \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("subscribe", "events") \
        .option("startingOffsets", "earliest") \
        .option("endingOffsets", "latest") \
        .load()

    purchase_events = raw_events \
        .select(raw_events.value.cast('string').alias('raw'),
                raw_events.timestamp.cast('string')) \
        .filter(is_purchase('raw'))

    extracted_purchase_events = purchase_events \
        .rdd \
        .map(lambda r: Row(timestamp=r.timestamp, **json.loads(r.raw))) \
        .toDF()
    extracted_purchase_events.printSchema()
    extracted_purchase_events.show()

    extracted_purchase_events.registerTempTable("extracted_purchase_events")

    spark.sql("""
        create external table purchases
        stored as parquet
        location '/tmp/purchases'
        as
        select * from extracted_purchase_events
    """)


if __name__ == "__main__":
    main()

```
## Run the above using the following 
```
docker-compose exec spark spark-submit /w205/assignment-12-anupjha10/write_hive_table.py

```

## Check if it wrote to HDFS 
```
docker-compose exec cloudera hadoop fs -ls /tmp/

docker-compose exec cloudera hadoop fs -ls /tmp/purchases/
```
## Output is 
```
science@w205s5-crook-4:~/w205/assignment-12-anupjha10$ docker-compose exec cloudera hadoop fs -ls /tmp/
Found 4 items
drwxrwxrwt   - mapred mapred              0 2016-04-06 02:26 /tmp/hadoop-yarn
drwx-wx-wx   - hive   supergroup          0 2019-04-16 08:44 /tmp/hive
drwxrwxrwt   - mapred hadoop              0 2016-04-06 02:28 /tmp/logs
drwxr-xr-x   - root   supergroup          0 2019-04-16 08:44 /tmp/purchases
science@w205s5-crook-4:~/w205/assignment-12-anupjha10$ docker-compose exec cloudera hadoop fs -ls /tmp/purchases/
Found 2 items
-rw-r--r--   1 root supergroup          0 2019-04-16 08:44 /tmp/purchases/_SUCCESS
-rw-r--r--   1 root supergroup       1645 2019-04-16 08:44 /tmp/purchases/part-00000-d96096d7-11c3-43ac-b454-5167e2f6529f-c000.snappy.parquet
science@w205s5-crook-4:~/w205/assignment-12-anupjha10$

```
## Query the data created in HDFS through presto
## First connect to Presto container providing the schema as default and catalog as hive
```
docker-compose exec presto presto --server presto:8080 --catalog hive --schema default

```

## Run the following 
```
show tables;
describe purchases;
select * from purchases;
```

## the output is 
```
presto:default> show tables;
   Table
-----------
 purchases
(1 row)

Query 20190416_084753_00002_2uish, FINISHED, 1 node
Splits: 2 total, 0 done (0.00%)
0:00 [0 rows, 0B] [0 rows/s, 0B/s]

presto:default> describe purchases;
   Column   |  Type   | Comment
------------+---------+---------
 accept     | varchar |
 host       | varchar |
 user-agent | varchar |
 event_type | varchar |
 timestamp  | varchar |
(5 rows)

Query 20190416_084810_00003_2uish, FINISHED, 1 node
Splits: 2 total, 1 done (50.00%)
0:00 [5 rows, 344B] [11 rows/s, 797B/s]

presto:default> select * from purchases;
 accept |       host        |   user-agent    |   event_type   |        timestamp
--------+-------------------+-----------------+----------------+-------------------------
 */*    | user1.comcast.com | ApacheBench/2.3 | purchase_sword | 2019-04-16 08:28:53.698
 */*    | user1.comcast.com | ApacheBench/2.3 | purchase_sword | 2019-04-16 08:28:53.706
 */*    | user1.comcast.com | ApacheBench/2.3 | purchase_sword | 2019-04-16 08:28:53.708
 */*    | user1.comcast.com | ApacheBench/2.3 | purchase_sword | 2019-04-16 08:28:53.71
 */*    | user1.comcast.com | ApacheBench/2.3 | purchase_sword | 2019-04-16 08:28:53.717
 */*    | user1.comcast.com | ApacheBench/2.3 | purchase_sword | 2019-04-16 08:28:53.725
 */*    | user1.comcast.com | ApacheBench/2.3 | purchase_sword | 2019-04-16 08:28:53.727
 */*    | user1.comcast.com | ApacheBench/2.3 | purchase_sword | 2019-04-16 08:28:53.732
 */*    | user1.comcast.com | ApacheBench/2.3 | purchase_sword | 2019-04-16 08:28:53.736
 */*    | user1.comcast.com | ApacheBench/2.3 | purchase_sword | 2019-04-16 08:28:53.738
 */*    | user2.att.com     | ApacheBench/2.3 | purchase_sword | 2019-04-16 08:29:12.323
 */*    | user2.att.com     | ApacheBench/2.3 | purchase_sword | 2019-04-16 08:29:12.328
 */*    | user2.att.com     | ApacheBench/2.3 | purchase_sword | 2019-04-16 08:29:12.332
 */*    | user2.att.com     | ApacheBench/2.3 | purchase_sword | 2019-04-16 08:29:12.341
 */*    | user2.att.com     | ApacheBench/2.3 | purchase_sword | 2019-04-16 08:29:12.345
 */*    | user2.att.com     | ApacheBench/2.3 | purchase_sword | 2019-04-16 08:29:12.348
 */*    | user2.att.com     | ApacheBench/2.3 | purchase_sword | 2019-04-16 08:29:12.351
 */*    | user2.att.com     | ApacheBench/2.3 | purchase_sword | 2019-04-16 08:29:12.355
 */*    | user2.att.com     | ApacheBench/2.3 | purchase_sword | 2019-04-16 08:29:12.357
 */*    | user2.att.com     | ApacheBench/2.3 | purchase_sword | 2019-04-16 08:29:12.361
(20 rows)

Query 20190416_084819_00004_2uish, FINISHED, 1 node
Splits: 2 total, 1 done (50.00%)
0:02 [20 rows, 1.61KB] [11 rows/s, 983B/s]

presto:default>

```
## Now create a spark streaming job which will continously write to HDFS every 10 seconds reading from kafka
## Following code would be run from the spark container 
```python
#!/usr/bin/env python
"""Extract events from kafka and write them to hdfs
"""
import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, from_json
from pyspark.sql.types import StructType, StructField, StringType


def purchase_sword_event_schema():
    """
    root
    |-- Accept: string (nullable = true)
    |-- Host: string (nullable = true)
    |-- User-Agent: string (nullable = true)
    |-- event_type: string (nullable = true)
    |-- timestamp: string (nullable = true)
    """
    return StructType([
        StructField("Accept", StringType(), True),
        StructField("Host", StringType(), True),
        StructField("User-Agent", StringType(), True),
        StructField("event_type", StringType(), True),
    ])


@udf('boolean')
def is_sword_purchase(event_as_json):
    """udf for filtering events
    """
    event = json.loads(event_as_json)
    if event['event_type'] == 'purchase_sword':
        return True
    return False


def main():
    """main
    """
    spark = SparkSession \
        .builder \
        .appName("ExtractEventsJob") \
        .getOrCreate()

    raw_events = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("subscribe", "events") \
        .load()

    sword_purchases = raw_events \
        .filter(is_sword_purchase(raw_events.value.cast('string'))) \
        .select(raw_events.value.cast('string').alias('raw_event'),
                raw_events.timestamp.cast('string'),
                from_json(raw_events.value.cast('string'),
                          purchase_sword_event_schema()).alias('json')) \
        .select('raw_event', 'timestamp', 'json.*')

    sink = sword_purchases \
        .writeStream \
        .format("parquet") \
        .option("checkpointLocation", "/tmp/checkpoints_for_sword_purchases") \
        .option("path", "/tmp/sword_purchases") \
        .trigger(processingTime="10 seconds") \
        .start()

    sink.awaitTermination()


if __name__ == "__main__":
    main()

```

## Run the streaming job using the following
```
docker-compose exec spark spark-submit /w205/assignment-12-anupjha10/write_swords_stream.py
```

## We will feed the streaming job by calling the flask api in a loop in mids container using apache bench
```
while true; do docker-compose exec mids ab -n 10 -H "Host: user1.comcast.com" http://localhost:5000/purchase_a_sword; done

```

## We check the streaming activity in HDFS 
```
docker-compose exec cloudera hadoop fs -ls /tmp/sword_purchases
```

## output is 
```
science@w205s5-crook-4:~/w205/assignment-12-anupjha10$ docker-compose exec cloudera hadoop fs -ls /tmp/sword_purchases
Found 17 items
drwxr-xr-x   - root supergroup          0 2019-04-16 09:00 /tmp/sword_purchases/_spark_metadata
-rw-r--r--   1 root supergroup       3644 2019-04-16 08:59 /tmp/sword_purchases/part-00000-1896ba30-a745-4be7-a59e-200786a98497-c000.snappy.parquet
-rw-r--r--   1 root supergroup        688 2019-04-16 08:56 /tmp/sword_purchases/part-00000-1caf4309-2b22-498e-b3da-219f250ed63c-c000.snappy.parquet
-rw-r--r--   1 root supergroup       3603 2019-04-16 08:58 /tmp/sword_purchases/part-00000-219ec47d-c590-4470-867e-bb7703887d34-c000.snappy.parquet
-rw-r--r--   1 root supergroup       3582 2019-04-16 08:59 /tmp/sword_purchases/part-00000-2351fbd2-5d91-4ef3-ad45-d98c5ce15973-c000.snappy.parquet
-rw-r--r--   1 root supergroup       2700 2019-04-16 08:58 /tmp/sword_purchases/part-00000-3051c8ca-98e1-44bd-acbe-ec829f7e47e3-c000.snappy.parquet
-rw-r--r--   1 root supergroup       3625 2019-04-16 08:59 /tmp/sword_purchases/part-00000-40bb1dda-2693-48cd-a1fd-5e0c6648c671-c000.snappy.parquet
-rw-r--r--   1 root supergroup       3595 2019-04-16 08:59 /tmp/sword_purchases/part-00000-588f7303-e9c0-4173-b4f9-35e68278c6e7-c000.snappy.parquet
-rw-r--r--   1 root supergroup       3512 2019-04-16 09:00 /tmp/sword_purchases/part-00000-6316dd7b-0fef-4659-88e3-0b37abb698a8-c000.snappy.parquet
-rw-r--r--   1 root supergroup       3559 2019-04-16 08:58 /tmp/sword_purchases/part-00000-672772d9-4e2a-400a-a698-f5d0a0e267f2-c000.snappy.parquet
-rw-r--r--   1 root supergroup       3646 2019-04-16 08:59 /tmp/sword_purchases/part-00000-808f4c1e-2c06-4e48-9bd7-05d50a73c396-c000.snappy.parquet
-rw-r--r--   1 root supergroup       3516 2019-04-16 09:00 /tmp/sword_purchases/part-00000-9201148e-feb8-4df3-988c-0799601696bd-c000.snappy.parquet
-rw-r--r--   1 root supergroup       3566 2019-04-16 09:00 /tmp/sword_purchases/part-00000-a3f58f8c-d4c1-46a3-b1d4-193e4bb244e5-c000.snappy.parquet
-rw-r--r--   1 root supergroup       3576 2019-04-16 08:59 /tmp/sword_purchases/part-00000-b568bc87-2751-4cd6-b5aa-eadeccfefb41-c000.snappy.parquet
-rw-r--r--   1 root supergroup       3620 2019-04-16 09:00 /tmp/sword_purchases/part-00000-df632f32-d50f-4099-91a6-845fd103c118-c000.snappy.parquet
-rw-r--r--   1 root supergroup       3599 2019-04-16 08:58 /tmp/sword_purchases/part-00000-e41bd71d-c481-47a1-8cb3-d808e1284005-c000.snappy.parquet
-rw-r--r--   1 root supergroup       3597 2019-04-16 09:00 /tmp/sword_purchases/part-00000-ec31f320-3e8d-4dcf-829d-37fe27fa13d7-c000.snappy.parquet
science@w205s5-crook-4:~/w205/assignment-12-anupjha10$

```
 
## We break the loop using ctrl+c and also use ctrl+c in spark streaming session and in flask session to quit everything 

## Bring down the cluster
```
 docker-compose down
```

## Check the status of the cluster
```
 docker-compose ps
 docker ps -a
```


