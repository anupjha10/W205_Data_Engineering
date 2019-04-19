# Anup Jha Annotations for Assignment 6
  ## Here First I change the directory to assignment directory which was cloned
  ```
   cd w205/assignment-06-anupjha10
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
  ## I bring up the docker cluster 
  ```
  docker-compose up -d
  ```
  ## Here I check the status of the containers in the docker cluster using docker-compose
  ```
  docker-compose ps
  ```
  ## Here I check the running containers using docker ps -a command
  ```
  docker ps -a
  ```
  ## I create a topic called 'foo' in the kafka container 
  ```
  docker-compose exec kafka kafka-topics --create --topic foo --partitions 1 --replication-factor 1 --if-not-exists --zookeeper zookeeper:32181
  ```
  ## I describe the topic created above in the kafka container
  ```
  docker-compose exec kafka kafka-topics --describe --topic foo --zookeeper zookeeper:32181
  ```
  ## Here I use several commands running in mids container to check the json file details
  ```
  docker-compose exec mids bash -c "cat /w205/assignment-06-anupjha10/assessment-attempts-20180128-121051-nested.json"
docker-compose exec mids bash -c "cat /w205/assignment-06-anupjha10/assessment-attempts-20180128-121051-nested.json | jq '.'"
docker-compose exec mids bash -c "cat /w205/assignment-06-anupjha10/assessment-attempts-20180128-121051-nested.json | jq '.[]' -c"
  ```
  ## Here I use the mids container to produce messages in kafka container from the json file using kafkacat
  ```
  docker-compose exec mids bash -c "cat /w205/assignment-06-anupjha10/assessment-attempts-20180128-121051-nested.json | jq '.[]' -c | kafkacat -P -b kafka:29092 -t foo && echo 'Produced 3280 messages.'"
  ```
  ## Here I consume the messages published above in the mids container using kafkacat
  ```
  docker-compose exec mids bash -c "kafkacat -C -b kafka:29092 -t foo -o beginning -e"
  ```
  ## Here I count the messages in mids container using the kafkacat . Consuming the published message again from the beginning
  ```
  docker-compose exec mids bash -c "kafkacat -C -b kafka:29092 -t foo -o beginning -e" | wc -l
  ```
  ## Here I tear down the cluster
  ```
  docker-compose down
  ```
  ## Here I take the history of the commands run 
  ```
  history > anupjha10-history.txt
  ```
  
