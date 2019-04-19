# Assignment 10

## Summary
 In this assignment I spun up a cluster with zookeeper,kafka,sparkand mids container.
 In the mids container I created api server using flask.  
 There were two flavors of flask api written.
 1) Simple : Here I log json messages into kafka using kafka producer api
 2) Complex : Here I log json messages with request headers aded into kafka using kafka producer api
 Then in the spark container using pyspark I consume the kafka messages 
 
 # Tasks

 I ran the following steps and commands to achieve the results

 ## Create the docker compose yaml file and then spin up the cluster with zookeeper, kafka and mids conatiner.
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

  spark:
    image: midsw205/spark-python:0.0.5
    stdin_open: true
    tty: true
    volumes:
      - ~/w205:/w205
    expose:
      - "8888"
    ports:
      - "8888:8888"
    extra_hosts:
      - "moby:127.0.0.1"
    command: bash

  mids:
    image: midsw205/base:0.1.8
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

 ## Created simple game api with following code
```python
#!/usr/bin/env python
import json
from flask import Flask
from kafka import KafkaProducer
app = Flask(__name__)
events_topic = 'events'
producer = KafkaProducer(bootstrap_servers='kafka:29092')

def log_to_kafka(topic, event):
        producer.send(topic, json.dumps(event).encode())

@app.route("/")
def default_response():
        default_event = {'event_type': 'default'}
        log_to_kafka('events', default_event)
        return "\nThis is the default response!\n"

@app.route("/buy_a_sword")
def purchase_sword():
        purchase_sword_event = {'event_type': 'purchase_sword'}
        log_to_kafka('events', purchase_sword_event)
        return "\nSword Purchased!\n"


@app.route("/join_guild/<guildname>")
def join_guild(guildname):
        #join the guild
        join_guild_event = {'event_type': 'joined_guild:%s'%(guildname)}
        log_to_kafka('events', join_guild_event)
        return ("\nJoined the Guild: %s\n" %(guildname))
```
 ## Run the simple game api using python and flask . It generates the return output for three urls first is default, second is buy a sword and third is join a guild with guild name specified in the url. These functions also log to kafka json messages
 ```
 docker-compose exec mids env FLASK_APP=/w205/assignment-10-anupjha10/simple_game_api.py flask run
 ```
 ## Test the simple_game_api using curl

 ```
 docker-compose exec mids curl http://localhost:5000/
 docker-compose exec mids curl http://localhost:5000/buy_a_sword
 docker-compose exec mids curl http://localhost:5000/join_guild/test_guild1
 ```
 ## The output of the test is the following
 ```
 science@w205s5-crook-4:~/w205/assignment-10-anupjha10$ docker-compose exec mids curl http://localhost:5000/
 This is the default response!
 
 science@w205s5-crook-4:~/w205/assignment-10-anupjha10$ docker-compose exec mids curl http://localhost:5000/buy_a_sword
 Sword Purchased!

 science@w205s5-crook-4:~/w205/assignment-10-anupjha10$ docker-compose exec mids curl http://localhost:5000/join_guild/test_guild1
 Joined the Guild: test_guild1
 ```
 ## Now read the events from kafka using kafkacat
 ```
 docker-compose exec mids kafkacat -C -b kafka:29092 -t events -o beginning -e
 ```
 ## We get the following output,which shows that json is getting logged as kafka message  
 ```
 {"event_type": "default"}
 {"event_type": "purchase_sword"}
 {"event_type": "joined_guild:test_guild1"}
 % Reached end of topic events [0] at offset 3: exiting
 ```
 ## Exit the simple game api using ctr+c

 
 ## Create the complex game api using the following code

 ```python
#!/usr/bin/env python
import json
from flask import Flask,request
from kafka import KafkaProducer
app = Flask(__name__)
events_topic = 'events'
producer = KafkaProducer(bootstrap_servers='kafka:29092')

def log_to_kafka(topic, event):
        event.update(request.headers)
		producer.send(topic, json.dumps(event).encode())

@app.route("/")
def default_response():
        default_event = {'event_type': 'default'}
        log_to_kafka('events', default_event)
        return "\nThis is the default response!\n"

@app.route("/buy_a_sword")
def purchase_sword():
        purchase_sword_event = {'event_type': 'purchase_sword'}
        log_to_kafka('events', purchase_sword_event)
        return "\nSword Purchased!\n"


@app.route("/join_guild/<guildname>")
def join_guild(guildname):
        #join the guild
        join_guild_event = {'event_type': 'joined_guild:%s'%(guildname)}
        log_to_kafka('events', join_guild_event)
        return ("\nJoined the Guild: %s\n" %(guildname))
 ```
 ## Run the complex game api which not only returns string to the http request but also logs the messages into kafka topic created.The messages are generated by the api server and logged into kafka topic. Whenever a http request is called the flask api server catches the request and calls the appropriate function. The function in turn publishes the messages to the kafka topic so that it can be consumed by the consumers of the kafka topic.The kafka messages are json format messages with http request header added into json
 ```
 docker-compose exec mids env FLASK_APP=/w205/assignment-10-anupjha10/complex_game_api.py flask run
 ```
 ## Test the complex game using curl

 ```
 docker-compose exec mids curl http://localhost:5000/
 docker-compose exec mids curl http://localhost:5000/buy_a_sword
 docker-compose exec mids curl http://localhost:5000/join_guild/test_guild1
 ```

 ## The output is

 ```
 science@w205s5-crook-4:~/w205/assignment-10-anupjha10$ docker-compose exec mids curl http://localhost:5000/

 This is the default response!

 science@w205s5-crook-4:~/w205/assignment-10-anupjha10$ docker-compose exec mids curl http://localhost:5000/buy_a_sword

 Sword Purchased!

 science@w205s5-crook-4:~/w205/assignment-10-anupjha10$ docker-compose exec mids curl http://localhost:5000/join_guild/test_guild1

 Joined the Guild: test_guild1

 ```
 ## Consume the messages created in kafka using kafkacat
 ```
 docker-compose exec mids bash -c "kafkacat -C -b kafka:29092 -t events -o beginning -e"
 ```
 ## The output is
 ```
 {"event_type": "default"}
 {"event_type": "purchase_sword"}
 {"event_type": "joined_guild:test_guild1"}
 {"Host": "localhost:5000", "event_type": "default", "Accept": "*/*", "User-Agent": "curl/7.47.0"}
 {"Host": "localhost:5000", "event_type": "purchase_sword", "Accept": "*/*", "User-Agent": "curl/7.47.0"}
 {"Host": "localhost:5000", "event_type": "joined_guild:test_guild1", "Accept": "*/*", "User-Agent": "curl/7.47.0"}
% Reached end of topic events [0] at offset 6: exiting

 ```
 ## We see that the api server is able to log the events in the kafka server. Different events generate different messages in the kafka queue of the topic.We also see that the request headers have been added to the events in the kafka messages.

 ## Bring up the spark shell 
 ```
 docker-compose exec spark pyspark
 ```
 
 ## Read from kafka in the spark session
 ```
 raw_events = spark.read.format("kafka").option("kafka.bootstrap.servers", "kafka:29092").option("subscribe","events").option("startingOffsets", "earliest").option("endingOffsets", "latest").load() 

 ```
 ## Explore the events 
 ```python
 events = raw_events.select(raw_events.value.cast('string'))
 import json
 extracted_events = events.rdd.map(lambda x: json.loads(x.value)).toDF()
 extracted_events.show()
 
 ```
 ## The output is 
 ```
+--------------------+
|          event_type|
+--------------------+
|             default|
|      purchase_sword|
|joined_guild:test...|
|             default|
|      purchase_sword|
|joined_guild:test...|
+--------------------+

 ```
 ## Exit the spark session using exit()
 
 ## Exit the complex game using ctrl+c

 ## Bring down the cluster
 ```
 docker-compose down
 ```
 ## Check the status of the cluster
 ```
 docker-compose ps
 docker ps -a
 ```
