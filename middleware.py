import subprocess
from threading import *
import time

def crack(currentHash, beginKey, endKey):
	
    if currentHash.hashtype is "NTLM":
       hashtype = 1000 #ntlm
    else:
       hashtype = 1000 #for now, just always do NTLM

    #get number of chars
    chars = int(currentHash.pwdlen)
    #maxKS size = chars^number
    maxKS = 26**chars

    #distributed commands
    beginKey = int(beginKey)
    endKey = int(endKey)
    
    #get total size of KS this node is responsible for
    if endKey < beginKey:    #it loops over n|0
       ksSize = maxKS-beginKey+endKey
    else:
       ksSize = endKey-beginKey

    chunk_size = int(ksSize/16)
    hash1 = currentHash.hashtext.lower()

    #create file of hash
    hfile = open(str(hash1[:4] + "..." + hash1[-4:]) + ".txt", 'w')
    hfile.write(hash1)
    hfile.close()

    pwd_str = ""
    for x in range(0, chars):
      pwd_str = pwd_str + "?l"  

    skipnum = beginKey
    limitnum = beginKey + chunk_size
    diff = limitnum-skipnum
    solved = False
    ksExhausted = False
    from chord_node import getStatus
    halt = getStatus()
    print (str(halt))
    while solved is False and ksExhausted is False and halt is False:
        #call hashcat (blocking)
        print ("Running hashcat process from " + str(skipnum) + " to " + str(limitnum) + " for len " + str(diff)) 
        sp = subprocess.Popen(['./hashcat-cli64.bin', '-m', str(hashtype), '-a 3', '-s', str(skipnum), '-l', str(diff), str(hash1) + ".txt", pwd_str], stdout=subprocess.PIPE)
        data, errdata = sp.communicate()
        data = str(data)
        halt = getStatus()

        #check if run was successful
        if "All hashes have been recovered" in data:
            data = data[data.find(hash1):]
            password = data[len(hash1)+1:data.find("\\n")]
            print ("We did it! Password is: " + password)
            solved = True
            #send message to superNode
            from chord_node import submitToSuperNode
            submitToSuperNode(password)
            from chord_node import tellSuccessorDone
            tellSuccessorDone() 
        
        #when keyspace is all searched
        if endKey > beginKey and limitnum >= endKey or skipnum < endKey and limitnum >= endKey:
           print ("Exhausted assigned keyspace")
           ksExhausted = True

        if limitnum == maxKS:
           skipnum = 0
           limitnum = chunk_size
        else:
           skipnum = limitnum+1
           limitnum = limitnum+chunk_size
        #print (str(skipnum) + " " + str(limitnum))
        
        if limitnum > maxKS:
           limitnum = maxKS 
    print ("Completed task")
