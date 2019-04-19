# Assignment 11

## Summary
 In this assignment I spun up a cluster with zookeeper,kafka,spark cloudera mids container.  
 In the mids container I created api server using flask.  
 In the kafka server I created a topic to which the messages are published by the flask app server.   
 These messages are then consumed in the spark container to stream the data .
 Also the extracted messages using pyspark is stored in hadoop as parquet file.  
 In the spark container the spark jobs two things :
   1) One of the jobs adds the request headers to the message 
   2) Another one filters the messages and shows the message

# Tasks

 I ran the following steps and commands to achieve the results

## Create the docker compose yaml file and then spin up the cluster with zookeeper, kafka, mids , spark and cloudera hadoop  container.
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
    image: midsw205/cdh-minimal:latest
    expose:
      - "8020" # nn
      - "50070" # nn http
      - "8888" # hue
    #ports:
    #- "8888:8888"
    extra_hosts:
      - "moby:127.0.0.1"

  spark:
    image: midsw205/spark-python:0.0.5
    stdin_open: true
    tty: true
    expose:
      - "8888"
    ports:
      - "8888:8888"
    volumes:
      - "~/w205:/w205"
    command: bash
    depends_on:
      - cloudera
    environment:
      HADOOP_NAMENODE: cloudera
    extra_hosts:
      - "moby:127.0.0.1"

  mids:
    image: midsw205/base:latest
    stdin_open: true
    tty: true
    expose:
      - "5000"
    ports:
      - "5000:5000"
    volumes:
      - "~/w205:/w205"
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


@app.route("/purchase_a_sword/<swordtype>")
def purchase_a_sword(swordtype):
    purchase_sword_event = {'event_type': 'purchase_sword-%s'%(swordtype)}
    log_to_kafka('events', purchase_sword_event)
    return "%s-Sword Purchased!\n"%(swordtype)
```
## Run the simple game api using python and flask . It generates the return output for default url, second is buy a sword with sword type specified in the url. These functions also log to kafka json messages
```
 docker-compose exec mids env FLASK_APP=/w205/assignment-11-anupjha10/game_api.py flask run --host 0.0.0.0
```
## Test the simple_game_api using browser on local machine. Since we have run the flask api using host 0.0.0.0 we can use ip address of the droplet on the browser  

```
 http://157.230.138.2:5000/purchase_a_sword/electric
```

## The output of the test is the following
```
electric-Sword Purchased!
```
 
## Now read the events from kafka using kafkacat
```
 docker-compose exec mids kafkacat -C -b kafka:29092 -t events -o beginning -e
```
## We get the following output,which shows that json is getting logged as kafka message  
```
{"Accept-Language": "en-US", "event_type": "purchase_sword-electric", "Host": "157.230.138.2:5000", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Upgrade-Insecure-Requests": "1", "Connection": "Keep-Alive", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134", "Accept-Encoding": "gzip, deflate"}
% Reached end of topic events [0] at offset 1: exiting
``` 

## We see that the api server is able to log the events in the kafka server. Different events generate different messages in the kafka queue of the topic.We also see that the request headers have been added to the events in the kafka messages. Also for purchase sword event the sword_type has been added.

## Now we will consume the events in spark container using pyspark code. Following is the pyspark code 
 
```python
#!/usr/bin/env python
"""Extract events from kafka and write them to hdfs
"""

import json
from pyspark.sql import SparkSession


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

    events = raw_events.select(raw_events.value.cast('string'))
    extracted_events = events.rdd.map(lambda x: json.loads(x.value)).toDF()

    extracted_events \
        .write \
        .parquet("/tmp/extracted_events")


if __name__ == "__main__":
    main()
```

## Run the pyspark code by following 
```
 docker-compose exec spark spark-submit /w205/assignment-11-anupjha10/extract_events.py
```
 
## check out results in hadoop

```
 docker-compose exec cloudera hadoop fs -ls /tmp/

 docker-compose exec cloudera hadoop fs -ls /tmp/extracted_events/
```
## Output is 
```
 science@w205s5-crook-4:~/w205/assignment-11-anupjha10$ docker-compose exec cloudera hadoop fs -ls /tmp/
Found 3 items
drwxr-xr-x   - root   supergroup          0 2019-04-05 06:28 /tmp/extracted_events
drwxrwxrwt   - mapred mapred              0 2018-02-06 18:27 /tmp/hadoop-yarn
drwx-wx-wx   - root   supergroup          0 2019-04-05 06:25 /tmp/hive
science@w205s5-crook-4:~/w205/assignment-11-anupjha10$ docker-compose exec cloudera hadoop fs -ls /tmp/extracted_events/
Found 2 items
-rw-r--r--   1 root supergroup          0 2019-04-05 06:28 /tmp/extracted_events/_SUCCESS
-rw-r--r--   1 root supergroup       4087 2019-04-05 06:28 /tmp/extracted_events/part-00000-01ef7c9d-b9ae-4dc0-a882-485244a4788e-c000.snappy.parquet
science@w205s5-crook-4:~/w205/assignment-11-anupjha10$
```

## In one more session run the log file for cloudera
```
docker-compose logs -f cloudera
```

## Now run another spark job which will add extra things such as 'Host' and 'Cache-Control' to the message consumed from kafka.
```python
#!/usr/bin/env python
"""Extract events from kafka and write them to hdfs
"""
import json
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import udf


@udf('string')
def munge_event(event_as_json):
    event = json.loads(event_as_json)
    event['Host'] = "moe"
    event['Cache-Control'] = "no-cache"
    return json.dumps(event)


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

    munged_events = raw_events \
        .select(raw_events.value.cast('string').alias('raw'),\
                raw_events.timestamp.cast('string')) \
        .withColumn('munged', munge_event('raw'))
    munged_events.show()

    extracted_events = munged_events \
        .rdd \
        .map(lambda r: Row(timestamp=r.timestamp, **json.loads(r.munged))) \
        .toDF()
    extracted_events.show()

    extracted_events \
        .write \
        .mode("overwrite") \
        .parquet("/tmp/extracted_events")


if __name__ == "__main__":
    main()

```

## Run the spark job using 
```
docker-compose exec spark spark-submit /w205/assignment-11-anupjha10/transform_events.py

``` 
## check out results in hadoop

```
 docker-compose exec cloudera hadoop fs -ls /tmp/

 docker-compose exec cloudera hadoop fs -ls /tmp/extracted_events/
```
## Output is 
```
 science@w205s5-crook-4:~/w205/assignment-11-anupjha10$ docker-compose exec cloudera hadoop fs -ls /tmp/
Found 3 items
drwxr-xr-x   - root   supergroup          0 2019-04-05 04:41 /tmp/extracted_events
drwxrwxrwt   - mapred mapred              0 2018-02-06 18:27 /tmp/hadoop-yarn
drwx-wx-wx   - root   supergroup          0 2019-04-05 04:34 /tmp/hive
science@w205s5-crook-4:~/w205/assignment-11-anupjha10$ docker-compose exec cloudera hadoop fs -ls /tmp/extracted_events/
Found 2 items
-rw-r--r--   1 root supergroup          0 2019-04-05 04:41 /tmp/extracted_events/_SUCCESS
-rw-r--r--   1 root supergroup       3846 2019-04-05 04:41 /tmp/extracted_events/part-00000-93429c1d-3dca-482e-a1f8-dd68f673ad2e-c000.snappy.parquet
science@w205s5-crook-4:~/w205/assignment-11-anupjha10$

```
 
## Now I will run another spark job which will filter the event type and show
```python
#!/usr/bin/env python
"""Extract events from kafka and write them to hdfs
"""
import json
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import udf


@udf('string')
def munge_event(event_as_json):
    event = json.loads(event_as_json)
    event['Host'] = "moe"
    event['Cache-Control'] = "no-cache"
    return json.dumps(event)


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

    munged_events = raw_events \
        .select(raw_events.value.cast('string').alias('raw'),
                raw_events.timestamp.cast('string')) \
        .withColumn('munged', munge_event('raw'))

    extracted_events = munged_events \
        .rdd \
        .map(lambda r: Row(timestamp=r.timestamp, **json.loads(r.munged))) \
        .toDF()

    electric_sword_purchases = extracted_events \
        .filter(extracted_events.event_type == 'purchase_sword-electric')
    electric_sword_purchases.show()
    # sword_purchases \
        # .write \
        # .mode("overwrite") \
        # .parquet("/tmp/sword_purchases")

    default_hits = extracted_events \
        .filter(extracted_events.event_type == 'default')
    default_hits.show()
    # default_hits \
        # .write \
        # .mode("overwrite") \
        # .parquet("/tmp/default_hits")


if __name__ == "__main__":
    main()
 
 
```

## run the spark job 
```
docker-compose exec spark spark-submit /w205/assignment-11-anupjha10/separate_events.py

```
## Output is
```
+--------------------+---------------+---------------+-------------+----------+----+-------------------------+--------------------+--------------------+--------------------+
|              Accept|Accept-Encoding|Accept-Language|Cache-Control|Connection|Host|Upgrade-Insecure-Requests|          User-Agent|          event_type|           timestamp|
+--------------------+---------------+---------------+-------------+----------+----+-------------------------+--------------------+--------------------+--------------------+
|text/html,applica...|  gzip, deflate|          en-US|     no-cache|Keep-Alive| moe|                        1|Mozilla/5.0 (Wind...|purchase_sword-el...|2019-04-05 07:07:...|
+--------------------+---------------+---------------+-------------+----------+----+-------------------------+--------------------+--------------------+--------------------+


+--------------------+---------------+---------------+-------------+----------+----+-------------------------+--------------------+----------+--------------------+
|              Accept|Accept-Encoding|Accept-Language|Cache-Control|Connection|Host|Upgrade-Insecure-Requests|          User-Agent|event_type|           timestamp|
+--------------------+---------------+---------------+-------------+----------+----+-------------------------+--------------------+----------+--------------------+
|text/html,applica...|  gzip, deflate|          en-US|     no-cache|Keep-Alive| moe|                        1|Mozilla/5.0 (Wind...|   default|2019-04-05 07:11:...|
|text/html,applica...|  gzip, deflate|          en-US|     no-cache|Keep-Alive| moe|                        1|Mozilla/5.0 (Wind...|   default|2019-04-05 07:11:...|
+--------------------+---------------+---------------+-------------+----------+----+-------------------------+--------------------+----------+--------------------+



```
## Bring down the cluster
```
 docker-compose down
```

## Check the status of the cluster
```
 docker-compose ps
 docker ps -a
```

