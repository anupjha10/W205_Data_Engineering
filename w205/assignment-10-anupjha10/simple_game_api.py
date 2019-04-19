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



