from flask import Flask, jsonify, request
from threading import Thread
import uuid
import os
import time
import asyncio

from net.ashost import sendSingleFile
from net.asclient import recvSingleFile, asClientOpenSockets, asClientTransfers, getConnectionSocket
from net.util.transfer import Transfer

app = Flask(__name__)

allTransfers = {}

@app.route("/")
def home():
	return jsonify({"message": "Ok"}), 200


@app.route("/recvSingle", methods = ["POST"])
async def recvSingle():
	remote = request.remote_addr
	if remote != '127.0.0.1': return jsonify({"message": "Forbidden"}), 403

	postParams = request.json

	transfer = newTransfer("client")
	allTransfers[transfer.tid] = transfer

	# Create socket connection
	connSocket = getConnectionSocket(transfer.tid, "0.0.0.0", 0)

	# Start listening for file in another thread
	recvCoroutine = recvSingleFile(transfer.tid, postParams["directory"], connSocket)

	return jsonify({"message": "ok", "listenPort": connSocket.getsockname()[1], "transferID": transfer.tid}), 200


@app.route("/knock")
def getPort():
	key =  list(asClientOpenSockets.keys())[0]
	return { "port": asClientOpenSockets[key].getsockname()[1] }, 200


@app.route("/sendSingle", methods = ["POST"])
async def sendSingle():
	remote = request.remote_addr
	if remote != '127.0.0.1': return jsonify({"message": "Forbidden"}), 403

	postParams = request.json

	transfer = newTransfer("host")
	allTransfers[transfer.tid] = transfer

	sendCoroutine = sendSingleFile(transfer.tid, postParams["file"], postParams["clientHost"], postParams["clientPort"])

	return jsonify({"message": "ok", "transferID": transfer.tid}), 200


@app.route("/transferProgress")
def transferProgress():
	remote = request.remote_addr
	if remote != '127.0.0.1': return jsonify({"message": "Forbidden"}), 403

	tid = request.args.get("tid")

	if not tid or tid not in allTransfers: return { "message": "Transfer not active" }, 404

	if allTransfers[tid].role == "client":
		if tid not in asClientTransfers:
			return {
				"tid": tid,
				"role": "client",
				"status": "inactive"
			}, 200

		transfer = asClientTransfers[tid]
		return {
			"tid": tid,
			"role": "client",
			"status": "active",
			"transferName": transfer.transferName,
			"totalBytes": transfer.totalBytes,
			"transferRate": transfer.currentTransferRate,
			"percentCompletion": transfer.percentCompletion()
		}, 200

	if allTransfers[tid].role == "host":
		return {
			message: "not implemented"
		}, 200

# private
	
def newTransfer(role):
	tid = uuid.uuid4().hex
	transfer = Transfer(tid, role)

	return transfer

app.run(port = 7836)