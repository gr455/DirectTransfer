# DirectTransfer
Send and recv files with people around you with ease and speed

DirectTransfer provides an easy way to share files with people around you or on the current network. It uses TCP over sockets to transfer files and folders, completely peer to peer. The aim of DirectTransfer is for user to be able to share files with as less clicks/keypresses as possible and quick.

As a user, there are two ways I can send files:

A send is initiated by me to a client, the client accepts the file
I expose an index of files that client can request from me, the client requests a file and I send it to them.

**It consists of two parts**:

**Daemon**: A simple HTTP server. All core network function calls are initiated by this server.

**UI**: talks to the daemon server for any actions.

## Usage

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

## Topology

![Untitled Diagram](https://user-images.githubusercontent.com/53974118/141684799-5d9c4104-44c4-499a-a32a-bccfbd8bd8ea.png)

