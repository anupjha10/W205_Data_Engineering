#!/usr/bin/env python
from flask import Flask
app = Flask(__name__)
events_topic = 'events'

@app.route("/")
def default_response():
    return "\nThis is the default response!\n"
	
@app.route("/buy_a_sword")
def purchase_sword():
    # business logic to purchase sword
	return "\nSword Purchased!\n"
	

@app.route("/join_guild/<guildname>")
def join_guild(guildname):
    #join the guild
    return ("\nJoined the Guild: %s\n" %(guildname))

    
