from threading import *
from socket import *
import pickle
from chord_node import *

MAX_CONNECTIONS = 20
MAX_RECV_SIZE = 4096
TIMEOUT = 10

def chord_rpc_listener(currentNode, rpc_handler):
	global serverSocket
	serverSocket = socket(AF_INET, SOCK_STREAM)
	addr = (currentNode.IpAddress, currentNode.port)
	serverSocket.bind((addr))
	serverSocket.listen(MAX_CONNECTIONS)
	print ("Started Waiting for Chord RPC Requests")
	while 1:
		conn, addr = serverSocket.accept() #accept the connection
		th = Thread(target=rpc_handler, args=(conn, addr))
		th.start()
	return


def serialize_message(message):
	return pickle.dumps(message)

def unserialize_message(serializedMessage):
	return pickle.loads(serializedMessage)

def send_packet(requestPacket, remoteNode):
	conn = socket(AF_INET, SOCK_STREAM)
	conn.settimeout(TIMEOUT)
	dst = (remoteNode.IpAddress, remoteNode.port)
	try:
		conn.connect((dst))
		conn.send(serialize_message(requestPacket))
		#print "Waiting to receive data from following node: "
		#print_node_ip_details(remoteNode)
		recvData = conn.recv(MAX_RECV_SIZE)
	except Exception as e:
		print (e)
		return None
	if recvData:
		try:
			replyMsg = unserialize_message(recvData)
		except:
			replyMsg = None
	else:
		replyMsg = None
	conn.shutdown(1)
	conn.close()
	return replyMsg

