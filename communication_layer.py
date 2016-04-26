from threading import *
from socket import *
import pickle
import sys
import os
from chord_node import *

MAX_CONNECTIONS = 20
MAX_RECV_SIZE = 4096
TIMEOUT = 5

def chord_rpc_listener(currentNode, rpc_handler):
	global serverSocket
	try:
			serverSocket = socket(AF_INET, SOCK_STREAM)
			#use private IP here
			ni.ifaddresses('eth0')
			ip = ni.ifaddresses('eth0')[2][0]['addr']
			addr = (ip, currentNode.port)
			serverSocket.bind((addr))
			serverSocket.listen(MAX_CONNECTIONS)
	except Exception as e:
		print ("[chord_rpc_listener] Exception while creating RPC Listener Thread")
		print (e)
		print ("[chord_rpc_listener] Exiting . . .")
		os._exit(1)
	print ("[chord_rpc_listener] Started Waiting for Chord RPC Requests")
	while 1:
		conn, addr = serverSocket.accept() #accept the connection
		th = Thread(target=rpc_handler, args=(conn, addr))
		th.start()
	return

def client_listener(ipaddr, rpc_handler):
	try:
		global serverSocket
		serverSocket = socket(AF_INET, SOCK_STREAM)
		#use private IP here
		ni.ifaddresses('eth0')
		ip = ni.ifaddresses('eth0')[2][0]['addr']
		addr = (ip, 838)
		serverSocket.bind((addr))
		serverSocket.listen(MAX_CONNECTIONS)
		print ("Waiting for the password...")
		while 1:
			conn, addr = serverSocket.accept() #accept the connection
			th = Thread(target=rpc_handler, args=(conn, addr))
			th.start()
		return
	except Exception as e:
		print ("socket already open, no biggie")

def serialize_message(message):
	return pickle.dumps(message)

def unserialize_message(serializedMessage):
	return pickle.loads(serializedMessage)

def send_packet(requestPacket, remoteNode):
	recvData = None
	conn = socket(AF_INET, SOCK_STREAM)
	conn.settimeout(TIMEOUT)
	dst = (remoteNode.IpAddress, remoteNode.port)
	try:
		conn.connect((dst))
		conn.send(serialize_message(requestPacket))
		#print ("Waiting to receive data from following node: ")
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

