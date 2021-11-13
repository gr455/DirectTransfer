import tqdm
import socket
import os
import json

from constants import CONSTANTS

# Sends file at @param filePath over TCP with the passed socket @param connSocket
def sendFile(filePath, connSocket):

	# Check if the file exists and system user has read permissions
	fileExists = checkFileExistence(filePath)
	if not fileExists: return { "status":  CONSTANTS.STATUS_FAIL_ENOENT }

	fileCanRead = getFilePerms(filePath)["read"]
	if not fileCanRead: return { "status":  CONSTANTS.STATUS_FAIL_ENOPERM }

	# First send file metadata
	fileMetadata = getFileMetadata(filePath)
	sendFileMetadata(connSocket, fileMetadata)

	# Now send file content
	progress = tqdm.tqdm(
		range(fileMetadata["bsize"]),
		f"Sending {fileMetadata['name']}", 
		unit = "B",
		unit_scale = True, 
		unit_divisor = 1024
	)

	with open(filePath, "rb") as file:
		iters = 0
		while True:
			iters += 1
			# If iterations reach over 1e9 (4 TB), something is probably wrong, abort
			if iters > 1e9:
				return { "status": CONSTANTS.STATUS_FAIL_TOOMANYITERS }
			# Read file bytes
			bytesRead = file.read(CONSTANTS.BUFFER_SIZE)
			# If no bytes were read, the file transfer is complete
			if not bytesRead:
				return { "status": CONSTANTS.STATUS_OK }

			# Send the read bytes
			connSocket.sendall(bytesRead)

			# Update progress bar
			progress.update(len(bytesRead))

# Sends a single file and closes the TCP connection
def sendSingleFile(filePath, clientHost, clientPort):
	# Create socket connection
	connSocket = getConnectionSocket(clientHost, clientPort)

	# Emit the file
	status = sendFile(filePath, connSocket)
	print("Done")
	# Close socket
	connSocket.close()

	return status

# Sends file metadata over TCP with passed socket
def sendFileMetadata(socket, fileMetadata):
	fileMetadataString = json.dumps(fileMetadata)
	socket.send(fileMetadataString.encode())

# Creates a socket to connect to client
def getConnectionSocket(clientHost, clientPort):
	sock = socket.socket()
	sock.connect((clientHost, clientPort))

	return sock

# Gets file permissions
def getFilePerms(filePath):
	perms = {}
	
	perms["read"] = os.access(filePath, os.R_OK)
	perms["write"] = os.access(filePath, os.W_OK)
	perms["exec"] = os.access(filePath, os.X_OK)

	return perms

# Checks if file exists
def checkFileExistence(filePath):
	return os.access(filePath, os.F_OK)

# Gets file metadata
def getFileMetadata(filePath):
	meta = {}

	meta["name"] = os.path.basename(filePath)
	meta["bsize"] = os.stat(filePath).st_size

	return meta

