import time
import signal
import sys
import copy
import random
from uuid import getnode as get_mac
import netifaces as ni
from hash_helper import *
import argparse
from threading import *
from communication_layer import *

####################### chord node definition #####################################
class chordNode():
	IpAddress = "localhost"
	port = 838
	nodeId = 0

	def __eq__(self, remote):
		if(self.nodeId == remote.nodeId and self.IpAddress == remote.IpAddress and self.port == remote.port):
			#print "[chordNode eq overloading ] Returning TRUE"
			return True
		return False

class hashSubmission():
	superNode = ""
	origNode = ""
	hashtype = ""
	hashtext = ""
	pwd_len = 0
	charset = ''

	def __init__(self, superNode, origNode, hashtype, hashtext, pwd_len, charset):
		self.superNode = superNode
		self.origNode = origNode
		self.hashtype = hashtype
		self.hashtext = hashtext
		self.pwd_len = pwd_len
		self.charset = charset

class chordMessageType():
		LOOK_UP_KEY_REQUEST = 1
		UPDATE_SUCCESSOR = 2
		UPDATE_PREDECESSOR = 3
		GET_PREDECESSOR = 4
		GET_SUCCESSOR = 5
		UPDATE_FINGER_TABLE = 6
		GET_CLOSEST_PRECEDING_FINGER = 7
		ACK = 8
		SUBMISSION_INFO = 9

class chordMessage():
	def __init__(self, messageSignature, message, extraMessage):
		self.messageSignature = messageSignature
		self.message = message
		self.extraMessage = extraMessage

currentNode = chordNode()
ni.ifaddresses('eth0')
ip = ni.ifaddresses('eth0')[2][0]['addr']
currentNode.IpAddress = ip
mac = get_mac()
currentHash = hashSubmission("", "", "", "", 0, '')
ksProgress = None

#Finger table
fingerTable = []
fingerTableLock = Lock()
predecessorNodeLock = Lock()

predecessor = currentNode

def submitToNetwork(remoteNode, hashInfo):
	requestPacket = chordMessage(chordMessageType.SUBMISSION_INFO, hashInfo, 0)
	reply = send_packet(requestPacket, remoteNode)
	if reply is None:
		print ("[submit to network] ***** FATAL **** Something went wrong")
		pass
	return

def updateProgress(ks_num):
        #print ("ks Num is: " + str(ks_num))        
        ksProgress = ks_num

def rpc_handler(conn, addr):
	global currentNode
	global currentHash
	requestMsg = conn.recv(MAX_RECV_SIZE)
	conn.settimeout(TIMEOUT)
	#(host, port) = conn.getsockanme()
	#print "Got a connection from " + str(addr)
	if requestMsg:
		request = unserialize_message(requestMsg)
		if request.messageSignature == chordMessageType.LOOK_UP_KEY_REQUEST:
			requestedKey = request.message
			#print "[rpc_handler]: Received Request to lookup Key: " + requestedKey.id_val
			tmpNode = look_up_key(request.message)
			replyMessage = chordMessage(chordMessageType.ACK, tmpNode, 0)
			conn.send(serialize_message(replyMessage))
			conn.close()
		elif request.messageSignature == chordMessageType.GET_PREDECESSOR:
			#print "[rpc_handler]: Received request to get Predecessor Node"
			node = get_curr_predecessor()
			replyMessage = chordMessage(chordMessageType.ACK, node, 0)
			conn.send(serialize_message(replyMessage))
			conn.close()

		elif request.messageSignature == chordMessageType.GET_SUCCESSOR:
			#print "[rpc_handler]: Received request to get Successor Node"
			node = get_immediate_successor()
			replyMessage = chordMessage(chordMessageType.ACK, node, 0)
			conn.send(serialize_message(replyMessage))
			conn.close()

		elif request.messageSignature == chordMessageType.UPDATE_PREDECESSOR:
			node = request.message
			#print "[rpc_handler]: My Predecessor will be set to following Node"
			#print_node_details(node)
			set_this_nodes_predecessor(node)
			replyMessage = chordMessage(chordMessageType.ACK, 0, 0)
			conn.send(serialize_message(replyMessage))
			conn.close()
		elif request.messageSignature == chordMessageType.UPDATE_SUCCESSOR:
			node = request.message
			#print "[rpc_handler]: My Successor will be set to following Node"
			#print_node_details(node)
			set_immediate_successor(node)
			replyMessage = chordMessage(chordMessageType.ACK, 0, 0)
			conn.send(serialize_message(replyMessage))
			conn.close()
		elif request.messageSignature == chordMessageType.GET_CLOSEST_PRECEDING_FINGER:
			requestedKey = request.message
			#print "[rpc_handler]: Received Request GET_NEXT_NODE_PRED, Key: " + requestedKey.id_val
			tmpNode = get_nearest_finger(requestedKey)
			replyMessage = chordMessage(chordMessageType.ACK, tmpNode, 0)
			conn.send(serialize_message(replyMessage))
			conn.close()
		elif request.messageSignature == chordMessageType.UPDATE_FINGER_TABLE:
			#print "[rpc_handler]: Received Request to Update Finger Table with Following Details:"
			#print "Index Entry: " + str(request.extraMessage)
			#print "Node to	 be Entered: "
			#print_node_details(request.message)
			update_current_nodes_finger_table(request.message, request.extraMessage)
			replyMessage = chordMessage(chordMessageType.ACK, 0, 0)
			conn.send(serialize_message(replyMessage))
			conn.close()
		elif request.messageSignature == chordMessageType.SUBMISSION_INFO:			
			hashItem = request.message
			print ("recvd a request..." + str(hashItem.hashtext))
			replyMessage = chordMessage(chordMessageType.ACK, 0, 0)
			conn.send(serialize_message(replyMessage))
			conn.close()
			#if this is a new hash
			if currentHash.hashtext != hashItem.hashtext:
				currentHash = hashItem
				tmpNode = get_immediate_successor()
				submitToNetwork(tmpNode, hashItem)

def get_curr_predecessor():
	global predecessor
	predecessorNodeLock.acquire()
	retNode = copy.deepcopy(predecessor)
	predecessorNodeLock.release()
	return retNode

def look_up_key(key):
	global currentNode
	# n' = find_predecessor(id)
	tmpNode = find_predecessor(key)
	# return n'.successor
	if tmpNode == currentNode:
		retNode = get_immediate_successor()
	else:
		retNode = rpc_get_successor(tmpNode)
	return retNode

def find_predecessor(key):
	global currentNode
	n_tmp = currentNode
	while 1:
		if n_tmp == currentNode:
			successor = get_immediate_successor()
		else:
			successor = rpc_get_successor(n_tmp)

		if hash_between_last_equal(key, n_tmp.nodeId, successor.nodeId):
			return n_tmp
		else:
			if n_tmp == currentNode:
				n_tmp = get_nearest_finger(key)
			else:
				n_tmp = rpc_closest_preceding_finger(key, n_tmp)
			if(n_tmp == currentNode):
				return n_tmp
	return None
def update_current_nodes_finger_table(node, index):
	global currentNode
	global fingerTable

	fingerTableLock.acquire()
	entry = fingerTable[index]
	fingerTableLock.release()
	
	if hash_between_first_equal(node.nodeId, currentNode.nodeId, entry.nodeId):
		fingerTableLock.acquire()
		if(node.nodeId.id_val != currentNode.nodeId.id_val):
			#print "[update_current_nodes_finger_table] index " + str(index) + " is updated to following node: "
			#print_node_details(node)
			#print "because node: " + str(node.nodeId.id_val) + " is between first equal node: " + str(currentNode.nodeId.id_val) + "and node: " + str(entry.nodeId.id_val) + " and it is not currentNode"
			fingerTable[index] = copy.deepcopy(node)
		fingerTableLock.release()
		remoteNode = get_curr_predecessor()		
		rpc_update_remote_nodes_finger_table(node, index, remoteNode)
	
##################################################################################
######################### CHORD NODE DATA STRUCTURE ##############################
##################################################################################
def get_nearest_finger(key):
	global fingerTable
	global currentNode
	fingerTableLock.acquire()
	for i in range((KEY_SIZE - 1), -1, -1):
		if hash_between(fingerTable[i].nodeId, currentNode.nodeId, key):
			tmpNode = copy.deepcopy(fingerTable[i])
			fingerTableLock.release()
			return tmpNode
	#this must be the closest node
	fingerTableLock.release()
	return copy.deepcopy(currentNode)

def init_finger_table():
	global fingerTable
	global currentNode

	fingerTableLock.acquire()
	for i in range(0, KEY_SIZE):
		tmpNode = copy.deepcopy(currentNode)
		fingerTable.append(tmpNode)
	fingerTableLock.release()
	return

def set_this_nodes_predecessor(node):
	global predecessor
	predecessorNodeLock.acquire()
	predecessor = copy.deepcopy(node)
	predecessorNodeLock.release()
	return

def set_immediate_successor(node):
	global fingerTable
	fingerTableLock.acquire()
	fingerTable[0] = copy.deepcopy(node)
	fingerTableLock.release()
	return

def get_immediate_successor():
	global fingerTable
	fingerTableLock.acquire()
	node = copy.deepcopy(fingerTable[0])
	fingerTableLock.release()
	return node

def set_remote_nodes_successor(remoteNode):
	requestPacket = chordMessage(chordMessageType.UPDATE_SUCCESSOR, currentNode, 0)
	#print "send_packet from set_remote_nodes_successor"
	reply = send_packet(requestPacket, remoteNode)
	if reply is None:
		print ("[set_remote_nodes_predecessor] ***** FATAL **** Something went wrong")
		pass
	return
	
def set_remote_nodes_predecessor(remoteNode):
	requestPacket = chordMessage(chordMessageType.UPDATE_PREDECESSOR, currentNode, 0)
	#print "send_packet from set_remote_nodes_predecessor"
	reply = send_packet(requestPacket, remoteNode)
	if reply is None:
		print ("[set_remote_nodes_predecessor] ***** FATAL **** Something went wrong")
		pass
	return

def rpc_get_predecessor(remoteNode):
	requestPacket = chordMessage(chordMessageType.GET_PREDECESSOR, 0, 0)
	#print "send_packet from rpc_get_predecessor"
	print_node_details(remoteNode)
	reply = send_packet(requestPacket, remoteNode)
	if reply is None:
		print ("[rpc_get_predecessor] ******* FATAL ****** Something is Worng")
		return None
	return reply.message

def rpc_get_successor(remoteNode):
	requestPacket = chordMessage(chordMessageType.GET_SUCCESSOR, 0, 0)
	#print "send_packet from rpc_get_successor"
	reply = send_packet(requestPacket, remoteNode)
	if reply is None:
		print ("[rpc_get_successor] ******* FATAL ***** Something went wrong")
		return None
	return reply.message
def rpc_closest_preceding_finger(key, remoteNode):
	requestPacket = chordMessage(chordMessageType.GET_CLOSEST_PRECEDING_FINGER, key, 0)
	#print "send_packet from rpc_closest_preceding_key"
	reply = send_packet(requestPacket, remoteNode)
	if reply is None:
		print ("[rpc_closest_preceding_finger] ****** FATAL **** Something is wrong")
		return None
	return reply.message
	
def rpc_lookup_key(remoteNode, key):
	requestPacket = chordMessage(chordMessageType.LOOK_UP_KEY_REQUEST, key, 0)
	#print "send_packet from rpc_lookup_key"
	reply = send_packet(requestPacket, remoteNode)
	if reply is None:
		print ("[rpc_lookup_key] ******FATAL ******   Something is wrong")
		return None
	return reply.message

#message between nodes, passed around to each node's successor
#def rpc_update_hash_info(remoteNode, currentHash)
#	requestPacket = chordMessage(chordMessageType.UPDATE_HASH_INFORMATION, currentHash, 0)
	#print ("send_packet from rpc_hash_info") 
	#reply = send_packet(requestPacket, 
        

def rpc_update_remote_nodes_finger_table(currentNode, i, remoteNode):
	requestedPacket = chordMessage(chordMessageType.UPDATE_FINGER_TABLE, currentNode, i)
	#print "send_packet from rpc_update_remote_nodes_finger_table"
	#print "[rpc_update_remote_nodes_finger_table] RPC to following node: "
	#print_node_details(remoteNode)
	#print "[rpc_update_remote_nodes_finger_table] index " + str(i) + " will be updated to following"
	#print_node_details(currentNode)
	reply = send_packet(requestedPacket, remoteNode)
	if reply is None:
		print ("[update_remote_nodes_finger_table] ******* FATAL ***** Something is Worng")
		pass
	return	
def update_others():
	#print "Do Nothing"
	#return
	global currentNode
	for i in range(0, KEY_SIZE):
		key = generate_bwd_entry_key(currentNode.nodeId, i)
		#print "[update_others] Finding Predecessor of Key: " + key.id_val
		remoteNode = find_predecessor(key)
		#print "[update_others] FOUND!!! Following is the node details"
		#print_node_details(remoteNode)
		#print "Predecessor of Key " + key.id_val + " is following node: "
		#print_node_details(remoteNode)
		if remoteNode != currentNode:
			rpc_update_remote_nodes_finger_table(currentNode, i, remoteNode)

def join(remoteNode):
	global fingerTable
	global currentNode
	
	#define successor finger[1].node
	#########################################################################
	#finger[1].node = remoteNode.find_successor(finger[1].start)
	startIndex = 0
	startKey = generate_fwd_entry_key(currentNode.nodeId, startIndex) # [for n+2^(i-1) where i starts from 1]
	tmpNode = rpc_lookup_key(remoteNode, startKey)
	if tmpNode is None:
		print ("[join] Couldn't find the node holding the key : " + startKey.id_val)
		exit(0)
	print ("[join] Following REMOTE NODE Contains the start key: " + startKey.id_val + " of this Node")
	print_node_details(tmpNode)
	print ("[join] Setting above REMOTE NODE as this node's immediate successor: ")

	set_immediate_successor(tmpNode) #Sets the 0th entry in the finger table
	#print_finger_table()
	#########################################################################

	#########################################################################
	#predecessor = successor.predecessor
	set_this_nodes_predecessor(rpc_get_predecessor(tmpNode))
	print ("[join] Setting following REMOTE NODE as this node's predecessor: ")
	print_node_details(predecessor)
	#########################################################################
	
	#########################################################################
	#successor.predecessor = n
	print ("[join] Setting this node as following REMOTE NODE's predecessor")
	print_node_details(tmpNode)
	set_remote_nodes_predecessor(tmpNode)
	#########################################################################
	set_remote_nodes_successor(predecessor)
	
	for i in range(1, KEY_SIZE):
		entryKey = generate_fwd_entry_key(currentNode.nodeId, i)

		fingerTableLock.acquire()
		prevNode = copy.deepcopy(fingerTable[i-1])	
		fingerTableLock.release()

		if hash_between_first_equal(entryKey, currentNode.nodeId, prevNode.nodeId):
			fingerTableLock.acquire()
			fingerTable[i] = copy.deepcopy(fingerTable[i-1])
			fingerTableLock.release()
		else:
			tmpNode = rpc_lookup_key(remoteNode, entryKey)
			fingerTableLock.acquire()
			fingerTable[i] = copy.deepcopy(tmpNode)
			fingerTableLock.release()
	#print "####   Before Update Others Printing FInger Table:  ##### "
	#print_finger_table()
	#########################################################################
	update_others()
	##########################################################################

def print_pred_succ_details():
	global fingerTable
	print ("###################################################")
	print ("Predecessor Details: ")
	print_node_details(get_curr_predecessor())
	print ("Successor Details: ")
	print_node_details(get_immediate_successor())
	print ("###################################################")
	
def print_node_details(node):
	print ("Node Id: " + str(node.nodeId.id_val) + " " + str(node.IpAddress) + ":" + str(node.port) + " ")
	print ("Node Id (int): " + str(int(node.nodeId.id_val,0)))

def print_node_ip_details(node):
	print ("IpAddress: " + str(node.IpAddress) + ":" + str(node.port) + " ")

def print_finger_table():
	global currentNode
	fingerTableLock.acquire()
	for i in range(0, KEY_SIZE):
		print ("Entry Key: " + str(generate_fwd_entry_key(currentNode.nodeId, i).id_val) + " Successor: " + str(fingerTable[i].nodeId.id_val) + " " + str(fingerTable[i].IpAddress) + ":" + str(fingerTable[i].port) )
		#print "Successor: " + str(fingerTable[i].IpAddress) + ":" + str(fingerTable[i].port) + " " + "Entry Key:" + str(generate_fwd_entry_key(currentNode.nodeId, i).id_val)
	fingerTableLock.release()
	print_pred_succ_details()
	return
	
######################## main function starts ###################################
def mainChord(config_str):
	global currentNode
	#parser = argparse.ArgumentParser(description='Welcome to the tool to build chord Network :-)')
	#parser.add_argument("-l", "--lookupNode", help="Existing node in IP:Port format")
	#parser.add_argument("-p", "--port", type=int, help="Port to listen on")

	#args = parser.parse_args()

	#if args.port is None:
	#	print ("Please specify the port to listen on with the -p option.")
	#	exit(0)
		
	#currentNode.port = args.port
	currentNode.port=838
	currentNode.submitterThreadPort=12221
	if "-l" in config_str:
		lookupNode = config_str[config_str.index("-l")+3:]
	else:
		lookupNode = None

	print ("[From Main]")
	print (ip, mac)
	currentNode.nodeId = generateHash(str(ip) + str(mac) + str(currentNode.port))
	#currentNode.nodeId = identifier(hex(args.val))

	print ("########### Node Details #######################################")
	print ("IP: " + currentNode.IpAddress)
	print ("Listening Port: " + str(currentNode.port))
	print ("ID: " + currentNode.nodeId.id_val)
	print ("################################################################")
	if lookupNode:
		print ("Lookup Node: " + lookupNode)
	else:
		print ("This is the first node joining in the network")

	init_finger_table()
	
	if lookupNode is None:
		set_this_nodes_predecessor(currentNode)
	
	#Start listener threads
	listenThread = Thread(target=chord_rpc_listener, args=(currentNode,rpc_handler))
	listenThread.daemon = True
	listenThread.start()
	time.sleep(1)

	if lookupNode is not None:
		#This is not the first node
		tmpNode = chordNode()
		tmpNode.IpAddress = lookupNode
		tmpNode.port = 838
		print ("######### Existing Contact Node Details ####################")
		print ("IP: " + lookupNode)
		print ("Port: " + str(tmpNode.port))
		print ("############################################################")
		join(tmpNode)

	
	while 1:
		listenThread.join(1)
		var = input()
		if var == 1:
			#print_pred_succ_details()
			print ("Key to search")
			val = input()
			tmpNode = look_up_key(identifier(hex(val)))
			print_node_details(tmpNode)	
		else:
			#print_finger_table()		
			print_pred_succ_details()
			#print_finger_table()		
	
if __name__ == "__main__":
	mainChord()

