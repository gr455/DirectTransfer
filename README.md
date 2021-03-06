# DirectTransfer
Send and recv files with people around you with ease and speed

DirectTransfer provides an easy way to share files with people around you or on the current network. It uses TCP over sockets to transfer files and folders, completely peer to peer. DirectTransfer allows the user to send or receive multiple files / folders with or from multiple devices at the same time, parallely.

## Flow

![Topology Diagram](https://user-images.githubusercontent.com/53974118/141687531-1e5d29ab-4cb3-466a-8156-43ce7544829d.png)

1. UI initiates a send (from the Host machine)
2. Host machine talks to the HTTP server of the Client machine, asking for an open TCP port
3. Client UI tells the Client HTTP server to open the TCP port
4. Client HTTP server queries to open a TCP port
5. Client HTTP server retrieves the opened port number
6. Client HTTP server sends the port number to Host HTTP server
7. Host HTTP server queries to send the file to the retrieved port
8. Host sends the file to the Client through the now established TCP connection

As a user, there are two ways I can send files:

A send is initiated by me to a client, the client accepts the file
I expose an index of files that client can request from me, the client requests a file and I send it to them.

**It consists of two parts**:

**Daemon**: A simple HTTP server. All core network function calls are initiated by this server.

**UI**: talks to the daemon server for any actions.

## Usage

To setup the development environment, first install all the dependencies

```
pip install -r requirements.txt
```

Then manually start the server

### Server (Development)
```
python daemon/server.py
```

Then use the CLI to interact with the server

### CLI

DirectTransfer provides a simple Command Line Interface to send files

```
python ui/cli/cli.py

Usage: cli.py [OPTIONS] ACTION

Actions:
  send: Send files to a client
  receive: Listen for files and reveive them
  
Options:
  -c TEXT  (send only) Client IP
  -p TEXT  File or directory path
  --help   Show this message and exit.

```

## Code

* `daemon/` contains all the code related to the daemon
  * `daemon/server.py` contains the code for the HTTP server written in Flask
  * `daemon/net/` contains all the TCP network code
    * `daemon/net/asclient.py` contains code for peer acting as a client (recieving files)
    * `daemon/net/ashost.py` contains code for peer acting as a host (sending files)

