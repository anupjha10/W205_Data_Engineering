  # Anup Jha Annotations for Assignment 5
  ## Here First I change the directory to W205 
  ```
   cd w205/
  ```
  ## Then I list the contents of the directory
  ```
    ls
  ```
  ## Here I clone the assignment 5 from github 
  ```
   git clone https://github.com/mids-w205-crook/assignment-05-anupjha10.git
  ```
  ## Now, I change the directory to the newly cloned directory
  ```
   cd assignment-05-anupjha10/
  ```
  ## Now, I list the Contents of the directory 
  ```
   ls
  ```  
  ## I check the exitsing branches of the repository 
  ```
   git branch
  ```
  ## Here I Create new branch in local git and name it Assignment 
  ```
    git branch Assignment
  ```
  ## Now I switch to the newly created branch
  ```
    git checkout Assignment
  ```
  ## I check the branches again to make sure that I am in Assignment branch
  ```
   git branch
  ```
  ## Now, I list the contents of the directory 
  ```
   ls
  ```
  ## Now, I create the docker compose Yaml file 
  ```
    vi docker-compose.yml
  ```
  ## I spawn the docker cluster in detached mode using docker-compose command 
  ```
   docker-compose up -d
  ```
  ## Here I go into the mids container and execute bash 
  ```
  docker-compose exec mids bash
  ```
  ## Here in the mids container I run the ipython
  ```
   ipython
  ```
  ## In the ipython environment I run the following to get the keys from redis container 
  ```
  import redis
  r = redis.Redis(host='redis', port='6379')
  r.keys()
  exit
  ```
  ## Now I exit from the mids container
  ```
   exit 
  ```
  ## Here I check the log of mids container in the cluster to get the jupyter notebook url
  ```
    docker-compose logs mids
  ```
  ## Here I call the curl command to download trips.csv file which will be used in python notebook to set key and values in Redis cluster
  ```
    curl -L -o trips.csv https://goo.gl/QvHLKe
  ```
  ## Here I tear down the cluster using docker-compose command 
  ```
    docker-compose down
  ```  
  ## Here I take the history of all commands ran by me and store it in file 
  ```
     history > anupjha10-history.txt
  ```
