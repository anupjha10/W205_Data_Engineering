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


