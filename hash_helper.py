import hashlib

class identifier():
	def __init__(self, id_val):
		self.id_val = id_val

	def __eq__(self, other):
		if self.id_val == other.id_val:
			return True
		return False

#key size because sha generates 160 bit key
KEY_SIZE = 160
#KEY_SIZE = 3

MAX_NUMBER_OF_NODES = (0x01 << 160)
#MAX_NUMBER_OF_NODES = (0x01 << 3)

def generateHash(ip):
	m = hashlib.sha1()
	ip = ip.encode('utf-8')	
	m.update(ip)
	return identifier("0x" + m.hexdigest())

def generate_offset(tableIndex):
	return identifier(hex(0x01 << tableIndex).replace("L", ""))

def generate_fwd_entry_key(currentKey, tableIndex):
	offset = generate_offset(tableIndex)
	val = (int(currentKey.id_val, 16) + int(offset.id_val, 16))%MAX_NUMBER_OF_NODES
	return identifier(hex(val).replace("L", ""))


def generate_bwd_entry_key(currentKey, tableIndex):
	offset = generate_offset(tableIndex)
	val = (int(currentKey.id_val, 16) - int(offset.id_val, 16))
	if(val < 0):
		val = MAX_NUMBER_OF_NODES + val
	return identifier(hex(val).replace("L", ""))

def hash_between_last_equal(h1, s1, s2):
	if (hash_equal(h1, s2)):
	        return True
	return hash_between(h1, s1, s2)

def hash_between_first_equal(h1, s1, s2):
	if(hash_equal(h1, s1)):
		return True
	return hash_between(h1, s1, s2)

#returns true if h1>h2
def hash_greater_than(h1, h2):
	if int(h1.id_val, 16) > int(h2.id_val, 16):
		return True
	return False

#returns true if h1<h2
def hash_less_than(h1, h2):
	if int(h1.id_val, 16) < int(h2.id_val, 16):
		return True
	return False

#returns true if h1==h2
def hash_equal(h1, h2):
	if int(h1.id_val, 16) == int(h2.id_val, 16):
		return True
	return False

def hash_between(h1, s1, s2):
	#if s1 == s2 then h1 must be between them assuming a full loop
	if(hash_equal(s1, s2)):
		return True

	#if h1 == s1 || h1 == s2 then return False
	if(hash_equal(h1, s1) or hash_equal(h1, s2)):
		return False

	#Check if s2 < s1 - if so assume a loop
	if hash_less_than(s2, s1):
		#assume a loop around the circle in which case h1 must be h1 > s1 || h1 < s2
		if hash_greater_than(h1, s1) or hash_less_than(h1, s2):
			return True
	else:
		#normal s1 < h1 < s2
		if hash_greater_than(h1, s1) and hash_less_than(h1, s2):
			return True

	return False

