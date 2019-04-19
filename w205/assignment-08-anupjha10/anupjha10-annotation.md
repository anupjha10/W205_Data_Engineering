# Anup Jha Annotations for Assignment 8
  ## Here I change directory to w205
  ```
  cd w205/
  ```
  ## Here I clone the assignment08 
  ```
  git clone https://github.com/mids-w205-crook/assignment-08-anupjha10.git
  ```
  ## Then I change the directory to Assignment 8
  ```
  cd assignment-08-anupjha10/
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
  ## I create a topic called "commits" in the kafka container. 
  ```
  docker-compose exec kafka kafka-topics --create --topic commits --partitions 1 --replication-factor 1 --if-not-exists --zookeeper zookeeper:32181
  ```
  ## I describe the topic created above in the kafka container
  ```
  docker-compose exec kafka kafka-topics --describe --topic commits --zookeeper zookeeper:32181
  ```
  ## Here I use several commands running in mids container to check the json file details
  ```
  docker-compose exec mids bash -c "cat /w205/assignment-08-anupjha10/assessment-attempts-20180128-121051-nested.json"
  docker-compose exec mids bash -c "cat /w205/assignment-08-anupjha10/assessment-attempts-20180128-121051-nested.json | jq '.'"
  docker-compose exec mids bash -c "cat /w205/assignment-08-anupjha10/assessment-attempts-20180128-121051-nested.json | jq '.[]' -c"
  ```
  ## Here I use the mids container to produce messages in kafka container from the json file using kafkacat to the topic created before
  ```
  docker-compose exec mids bash -c "cat /w205/assignment-08-anupjha10/assessment-attempts-20180128-121051-nested.json | jq '.[]' -c | kafkacat -P -b kafka:29092 -t commits && echo 'Produced 3280 messages.'"
  ```
  ## Here I consume the messages published above in the mids container using kafkacat
  ```
  docker-compose exec mids bash -c "kafkacat -C -b kafka:29092 -t commits -o beginning -e"
  ```
  ## Here I count the messages in mids container using the kafkacat . Consuming the published message again from the beginning
  ```
  docker-compose exec mids bash -c "kafkacat -C -b kafka:29092 -t commits -o beginning -e" | wc -l
  ```
  ## Now,I use Pyspark to read the messages from kafka and look at the messages and write to HDFS. For that first below I start the pyspark in spark container
  ```
  docker-compose exec spark pyspark
  ```
  ## In the pyspark session I read the messages from the kafka server from the topic created above
  ```
   import json
   raw_commits = spark.read.format("kafka").option("kafka.bootstrap.servers", "kafka:29092").option("subscribe","commits").option("startingOffsets", "earliest").option("endingOffsets", "latest").load() 
   raw_commits.cache()
  ```
  ## Here I check the schema of raw_commits
  ```
   raw_commits.printSchema()
  ```
  ## Here I take the value from the message got from kafka and create another data frame
  ```
   commits = raw_commits.select(raw_commits.value.cast('string'))
  ```
  ## Here I print the schema of new DataFrame
  ```
    commits.printSchema()
  ```
  ## Here I write the Data Frame to HDFS as parquet file 
  ```
   commits.write.parquet("/tmp/commits")
  ```
  ## In another window with duplicated session I check the HDFS container to list the directory and check if parquet file was created or not 
  ```
  docker-compose exec cloudera hadoop fs -ls /tmp/
  docker-compose exec cloudera hadoop fs -ls /tmp/commits/
  ```
  ## Back in pyspark session I load the commits DF into another DF by loading as json using map and lambda function 
   ```
    extracted_commits = commits.rdd.map(lambda x: json.loads(x.value)).toDF()
   ```
  ## Here I check the first 20 rows of the Data Frame 
   ```  
	extracted_commits.show()
   ```
  ## Here I register the Data Frame as temp table so that SQL can be executed using that 
  ```
   extracted_commits.registerTempTable('commits')
  ```
  ## Here using Spark SQL unravel the complex nested json and show first 10 rows for thr value we want to extract  
  ```
  spark.sql("select sequences.questions[0].user_incomplete as user_incomplete from commits limit 10").show()
  ```
  ## Here I store the SQL output as another DataFrame
  ```
    some_commit_info = spark.sql("select sequences.questions[0].user_incomplete as user_incomplete from commits limit 10")
  ```
  ## Here I check the contents of the new Data Frame created 
  ```
    some_commit_info.show()
  ```
  ## Here I write this Data Frame as parquet format into HDFS
  ```
   some_commit_info.write.parquet("/tmp/some_commit_info")
  ```
  ## In the other window I check the directory listing in HDFS container to see if the parquet file was created 
  ```
   docker-compose exec cloudera hadoop fs -ls /tmp/
   docker-compose exec cloudera hadoop fs -ls /tmp/some_commit_info/
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
  
