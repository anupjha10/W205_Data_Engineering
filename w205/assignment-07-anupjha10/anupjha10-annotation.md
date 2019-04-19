# Anup Jha Annotations for Assignment 7
  ## Here I change directory to w205
  ```
  cd w205/
  ```
  ## Here I clone the assignment07 
  ```
  git clone https://github.com/mids-w205-crook/assignment-07-anupjha10.git
  ```
  ## Then I change the directory to assignment 7
  ```
  cd assignment-07-anupjha10/
  ```
  ## I create a new branch called Assignment in my local git copy 
  ```
  git branch Assignment
  ```
  ## I checkout to the newly created branch 
  ```
  git checkout Assignment
  ```
  ## Here I get the json data which we want to publish
  ```
  curl -L -o assessment-attempts-20180128-121051-nested.json https://goo.gl/ME6hjp
  ```
  
  ## I list the contents to see if the file has been copied using curl
  ```
  ls
  ```
  ## Then I create the docker compose yaml file 
  ```
  vi docker-compose.yml
  ```
  ## Here using the jq tool I count the number of messages in the json file
  ```
  jq length assessment-attempts-20180128-121051-nested.json
  ```
  ## Here I create a file which creates the json file in pretty format using jq
  ```
  jq '.[]' assessment-attempts-20180128-121051-nested.json > pretty_assessment.json
  ```
  ## I bring up the docker cluster 
  ```
  docker-compose up -d
  ```
  ## In one more duplicated session I run the following to check the log messages in kafka
  ```
  docker-compose logs -f kafka
  ```
  ## Here I check the status of the containers in the docker cluster using docker-compose
  ```
  docker-compose ps
  ```
  ## Here I check the running containers using docker ps -a command
  ```
  docker ps -a
  ```
  ## I create a topic called "user\_actions\_web\_log" in the kafka container. I do get a warning that since I am using "\_" in the topic name so either to use "\_" or "." in the topic name but not both as otherwise it will conflict with each other 
  ```
  docker-compose exec kafka kafka-topics --create --topic user_actions_web_log --partitions 1 --replication-factor 1 --if-not-exists --zookeeper zookeeper:32181
  ```
  ## I describe the topic created above in the kafka container
  ```
  docker-compose exec kafka kafka-topics --describe --topic user_actions_web_log --zookeeper zookeeper:32181
  ```
  ## Here I use several commands running in mids container to check the json file details
  ```
  docker-compose exec mids bash -c "cat /w205/assignment-07-anupjha10/assessment-attempts-20180128-121051-nested.json"
  docker-compose exec mids bash -c "cat /w205/assignment-07-anupjha10/assessment-attempts-20180128-121051-nested.json | jq '.'"
  docker-compose exec mids bash -c "cat /w205/assignment-07-anupjha10/assessment-attempts-20180128-121051-nested.json | jq '.[]' -c"
  ```
  ## Here I use the mids container to produce messages in kafka container from the json file using kafkacat to the topic created before
  ```
  docker-compose exec mids bash -c "cat /w205/assignment-07-anupjha10/assessment-attempts-20180128-121051-nested.json | jq '.[]' -c | kafkacat -P -b kafka:29092 -t user_actions_web_log && echo 'Produced 3280 messages.'"
  ```
  ## Here I consume the messages published above in the mids container using kafkacat
  ```
  docker-compose exec mids bash -c "kafkacat -C -b kafka:29092 -t user_actions_web_log -o beginning -e"
  ```
  ## Here I count the messages in mids container using the kafkacat . Consuming the published message again from the beginning
  ```
  docker-compose exec mids bash -c "kafkacat -C -b kafka:29092 -t user_actions_web_log -o beginning -e" | wc -l
  ```
  ## Now,I use Pyspark to read the messages from kafka and look at the messages. For that first below I start the pyspark in spark container
  ```
  docker-compose exec spark pyspark
  ```
  ## In the pyspark session I read the messages from the kafka server from the topic created above
  ```
  messages = spark.read.format("kafka").option("kafka.bootstrap.servers", "kafka:29092").option("subscribe","user_actions_web_log").option("startingOffsets", "earliest").option("endingOffsets", "latest").load() 
 ```
  ## I check the schema of the messages DataFrame
  ```
  messages.printSchema()
  ```
  ## Then I check the first 20 rows 
  ```
   messages.show()
  ```
  ## Then I create another data frame where I take the key and value from the original message and cast them as strings
  ```
  messages_as_strings=messages.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")
  ```
  ## Then I take a look at this new data frame
  ```
  messages_as_strings.show()

  messages_as_strings.printSchema()

  messages_as_strings.count()
  ```
  ## Then I create a selectable view from the data frame so that I can run spark sql 
  ```
   messages_as_strings.createOrReplaceTempView("messages_as_strings")
  ```
  ## Then I run the sppark sql to get the "value" column from the first row of the data frame 
  ```
   spark.sql("SELECT value from messages_as_strings").take(1)
  ```
  ## Now I use the json package to look at the message in json format
  ```
   messages_as_strings.select('value').take(1)

   messages_as_strings.select('value').take(1)[0].value

   import json

   first_message=json.loads(messages_as_strings.select('value').take(1)[0].value)

   first_message

   print(first_message['sequences']['questions'][0]['options'][0]['id'])
  
  ```
  ## Here I tear down the cluster
  ```
  docker-compose down
  ```
  ## Here I check the cluster status after tearing down 
  ```
  docker-compose ps
  ```
  ## Here I check the status of the containers using docker command 
  ```
  docker ps -a
  ```
  ## Here I take the history of the commands run 
  ```
   history > anupjha10-history.txt
  ```
  
