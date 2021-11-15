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

	if not pingSelfServer(): return click.echo(click.style("Fatal: Daemon server is not running. Aborting", fg="red"))
	click.echo(click.style("[+] Daemon Server running", fg="green"))
	if not pingPeerServer(clientHost): return print("[-] Peer did not respond. Aborting")
	click.echo(click.style("[+] Client up, knocking for port", fg="green"))

	# knock knock knocking on client's door. Get port
	knock = requests.get(f"{clientHttpServer}/knock")
	port = json.loads(knock.text)["port"]

	click.echo(click.style("[+] Client port retrieved", fg="green"))

	sendRequest = {"file": filePath, "clientHost": clientHost, "clientPort": port}

	requests.post(f"{selfHttpServer}/sendSingle", json = sendRequest)
	click.echo(click.style("[+] Sending file", fg="green"))


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

	totalBytes = transfer["totalBytes"]

	while True:
		pastCompletedBytes = transfer["completedBytes"] 
		transferResponse = requests.get(f"{selfHttpServer}/transferProgress?tid={transferID}")
		transfer = json.loads(transferResponse.text)

		if transfer["status"] == "inactive":
			progress.update(totalBytes - pastCompletedBytes)
			click.echo(click.style("\n[+] Transfer finished", fg="green"))
			break

		progress.update(transfer["completedBytes"] - pastCompletedBytes)
		time.sleep(0.5)				




@click.command()
@click.argument("action")
@click.option("-c", type = str, help = "(send only) Client IP")
@click.option("-p", type = str, help = "File or directory path")
def cli(action, c, p):
	if action == "send":
		if not c: return click.echo(click.style("Fatal: No client IP passed", fg="red"))
		if not p: return click.echo(click.style("Fatal: No file path passed", fg="red"))
		try: sendFile(p, c)
		except Exception as e: click.echo(click.style("Fatal: Something went wrong while transferring", fg="red"))

	elif action == "receive":
		if not p: return click.echo(click.style("Fatal: No directory path passed", fg="red"))
		try: recieveFile(p)
		except Exception as e: click.echo(click.style("Fatal: Something went wrong while transferring", fg="red"))

	else:
		click.echo(click.get_current_context().get_help())

if __name__ == '__main__':
	cli()