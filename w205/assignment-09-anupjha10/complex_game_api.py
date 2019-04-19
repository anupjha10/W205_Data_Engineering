#!/usr/bin/env python
from kafka import KafkaProducer
from flask import Flask
app = Flask(__name__)
event_logger = KafkaProducer(bootstrap_servers='kafka:29092')
events_topic = 'events'

@app.route("/")
def default_response():
    event_logger.send(events_topic, 'default'.encode())
    return "\nThis is the default response!\n"
	
@app.route("/buy_a_sword")
def purchase_sword():
    # business logic to purchase sword
    event_logger.send(events_topic, 'Sword Purchased!'.encode())
    return "\nSword Purchased!\n"
	

@app.route("/join_guild/<guildname>")
def join_guild(guildname):
    #join the guild
    # log event to kafka
    event_logger.send(events_topic, ("Joined the Guild: %s" %(guildname)).encode())
    return ("\nJoined the Guild: %s\n" %(guildname))


