#!/usr/bin/env python
import subprocess
import time

def crack(hash_type, hash_len, char_set, hash_text):
	
    if hash_type is "NTLM":
       hashtype = 1000 #ntlm
    else:
       hashtype = 1000 #for now, just always do NTLM

    attack = 3 #for now, always use brute force
    #get number of chars
    chars = int(hash_len)
    #maxKS size = chars^number
    maxKS = 26**chars

    #distributed commands
    skipnum = 0
    limitnum = int(maxKS/8)
    chunk_size = int(maxKS/8)
    
    
    charstyle = "l"
    
    hash1 = hash_text.lower()

    #create file of hash
    hfile = open('hash.txt', 'w')
    hfile.write(hash1)
    hfile.close()

    pwd_str = ""
    for x in range(0, chars):
      pwd_str = pwd_str + "?l"  
    #print (pwd_str)
      
    solved = False
    while solved is False:
        #call hashcat (blocking)
        print ("Running hashcat process from " + str(skipnum) + " to " + str(limitnum)) 
        sp = subprocess.Popen(['./hashcat-cli64.bin', '-m', str(hashtype), '-a', str(attack), '-s', str(skipnum), '-l', str(limitnum), 'hash.txt', pwd_str], stdout=subprocess.PIPE)
        data, errdata = sp.communicate()
        data = str(data)

        #check if run was successful
        if "All hashes have been recovered" in data:
            data = data[data.find(hash1):]
            password = data[len(hash1)+1:data.find("\\n")]
            print ("We did it! Password is: " + password)
            solved = True
        
        skipnum = limitnum+1
        limitnum = limitnum+chunk_size
        #print (str(skipnum) + " " + str(limitnum))
        if limitnum > maxKS:
           limitnum = maxKS
    print ("Completed task")
