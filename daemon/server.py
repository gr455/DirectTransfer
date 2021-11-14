from flask import Flask, jsonify, request
from threading import Thread
import uuid
import os
import time
import asyncio

from net.ashost import sendSingleFile
from net.asclient import recvSingleFile, asClientOpenSockets, getConnectionSocket

app = Flask(__name__)

@app.route("/")
def home():
	return jsonify({"message": "Ok"}), 200

@app.route("/recvSingle", methods = ["POST"])
async def recvSingle():
	remote = request.remote_addr
	if remote != '127.0.0.1': return jsonify({"message": "Forbidden"}), 403

	connId = uuid.uuid4().hex
	# Create socket connection
	connSocket = getConnectionSocket(connId, "0.0.0.0", 0)

	# Start listening for file in another thread
	recvCoroutine = recvSingleFile(connId, "/home/grass/tstst", connSocket)

	return jsonify({"message": "ok", "listenPort": connSocket.getsockname()[1]}), 200


@app.route("/getPort/<connId>")
def getPort():
	return {"port": asClientOpenSockets[connId].getsockname()[1]}


app.run(port = 7836)