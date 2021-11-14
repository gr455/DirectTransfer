import requests
import click
import os
import json
import time
import tqdm

DAEMON_HTTP_SERVER_PORT = 7836

def pingSelfServer():
	try:
		return requests.get(f"http://0.0.0.0:{DAEMON_HTTP_SERVER_PORT}").status_code == 200
	except requests.exceptions.ConnectionError:
		return False

def pingPeerServer(peerHost):
	try:
		return requests.get(f"http://{peerHost}:{DAEMON_HTTP_SERVER_PORT}").status_code == 200
	except requests.exceptions.ConnectionError:
		return True

def sendFile(filePath, clientHost):

	clientHttpServer = f"http://{clientHost}:{DAEMON_HTTP_SERVER_PORT}"
	selfHttpServer = f"http://0.0.0.0:{DAEMON_HTTP_SERVER_PORT}"
	# knock knock knocking on client's door. Get port

	if not pingSelfServer(): return print("[-] Daemon server is not running. Aborting")
	print("[+] Daemon Server running")
	if not pingPeerServer(clientHost): return print("[-] Peer did not respond. Aborting")
	print("[+] Client up, knocking for port")

	knock = requests.get(f"{clientHttpServer}/knock")
	port = json.loads(knock.text)["port"]

	print("[+] Client port retrieved")

	sendRequest = {"file": filePath, "clientHost": clientHost, "clientPort": port}

	requests.post(f"{selfHttpServer}/sendSingle", json = sendRequest)
	print("[+] Sending file")	


def recieveFile(directoryPath = "."):

	selfHttpServer = f"http://0.0.0.0:{DAEMON_HTTP_SERVER_PORT}"

	recvRequest = {"directory": directoryPath}

	response = requests.post(f"{selfHttpServer}/recvSingle", json = recvRequest)
	responseObject = json.loads(response.text)

	transferID = responseObject["transferID"]
	
	# time.sleep(2)

	transferResponse = requests.get(f"{selfHttpServer}/transferProgress?tid={transferID}")
	transfer = json.loads(transferResponse.text)

	while True:
		if transferResponse.status_code == 200 and ("status" in transfer and transfer["status"] == "active"):
			break

		transferResponse = requests.get(f"{selfHttpServer}/transferProgress?tid={transferID}")
		transfer = json.loads(transferResponse.text)
		time.sleep(1)

	progress = tqdm.tqdm(
		range(transfer["totalBytes"]),
		f"Recieving {transfer['transferName']}",
		unit = "B",
		unit_scale = True,
		unit_divisor = 1024
	)

	while True:
		pastCompletedBytes = transfer["completedBytes"] 
		transferResponse = requests.get(f"{selfHttpServer}/transferProgress?tid={transferID}")
		transfer = json.loads(transferResponse)

		if transfer["status"] == "inactive":
			progress.update(transfer["totalBytes"] - pastCompletedBytes)
			break

		progress.update(transfer["completedBytes"] - pastCompletedBytes)
		time.sleep(1)				




@click.command()
@click.argument("action")
@click.option("-c", type = str, help = "(send only) Client IP")
@click.option("-p", type = str, help = "File or directory path")
def cli(action, c, p):
	if action == "send":
		if not c: click.echo(click.style("Error", fg="red") + ": No client IP passed")
		if not p: click.echo(click.style("Error", fg="red") + ": No file path passed")
		sendFile(p, c)

	elif action == "receive":
		if not p: click.echo(click.style("Error", fg="red") + ": No directory path passed")
		recieveFile(p)

	else:
		click.echo(click.get_current_context().get_help())

if __name__ == '__main__':
	cli()