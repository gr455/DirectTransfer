import socket
import os
import json
import asyncio

from net.util.progress import Progress
from constants import CONSTANTS

asClientOpenSockets = {} # "<id>": <socket object> 
asClientTransfers = {}

def fire_and_forget(f):
	def wrapped(*args, **kwargs):
		return asyncio.get_event_loop().run_in_executor(None, f, *args, *kwargs)

	return wrapped

# Listens for file to be saved at @param directoryPath with the passed socket 
# @param connSocket
def recvFile(connId, directoryPath, connSocket):

	# Check if system user can write to the given directory and it exists
	directoryExists = checkDirectoryExistence(directoryPath)
	if not directoryExists: return { "status": CONSTANTS.STATUS_FAIL_ENOENT }

	directoryCanWrite = getFilePerms(directoryPath)["write"]
	if not directoryCanWrite: return { "status": CONSTANTS.STATUS_FAIL_ENOPERM }

	hostSocket, hostAddress = connSocket.accept()

	# Client will first recieve metadata in JSON format
	metadata = hostSocket.recv(CONSTANTS.BUFFER_SIZE).decode()
	metadata = json.loads(metadata)

	if not "name" in metadata or not "bsize" in metadata:
		return { "status": CONSTANTS.STATUS_FAIL_INCOMPMETA }

	fileName = os.path.basename(metadata["name"])
	filePath = os.path.join(directoryPath, fileName)
	fileSize = int(metadata["bsize"])

	progress = Progress(fileSize, fileName)
	asClientTransfers[connId] = progress

	with open(filePath, "wb") as file:
		iters = 0
		while True:
			iters += 1
			# If iterations reach over 1e9 (4 TB), something is probably wrong, abort
			if iters > 1e9:
				return { "status": CONSTANTS.STATUS_FAIL_TOOMANYITERS }

			bytesRecvd = hostSocket.recv(CONSTANTS.BUFFER_SIZE)

			# If no bytes were recvd, the file transfer is complete
			if not bytesRecvd:
				return { "status": CONSTANTS.STATUS_OK }

			# Write recieved bytes to file
			file.write(bytesRecvd)

			# Update progress bar
			progress.update(len(bytesRecvd))


# Listens for and recieves one single file by a transfer
@fire_and_forget
def recvSingleFile(connId, directoryPath, connSocket):
	# Recv the file
	status = recvFile(connId, directoryPath, connSocket)

	# Close socket
	connSocket.close()
	del asClientOpenSockets[connId]
	del asClientTransfers[connId]

	return status

def getConnectionSocket(connId, clientHost, clientPort):
	sock = socket.socket()
	sock.bind((clientHost, clientPort))
	sock.listen(CONSTANTS.MAX_SOCKET_QUEUE)

	asClientOpenSockets[connId] = sock

	return sock

# Gets file permissions
def getFilePerms(filePath):
	perms = {}
	
	perms["read"] = os.access(filePath, os.R_OK)
	perms["write"] = os.access(filePath, os.W_OK)
	perms["exec"] = os.access(filePath, os.X_OK)

	return perms


def checkDirectoryExistence(directoryPath):
	return os.access(directoryPath, os.F_OK) and os.path.isdir(directoryPath)
