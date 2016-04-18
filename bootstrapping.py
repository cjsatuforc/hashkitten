#!/usr/bin/env python
import requests
from datetime import datetime
import json

#
# Small dnsimple API to handle bootstrapping
# getPeerIP() : fetches the DNS record, and returns back IP address, times they joined and record ID
# postHostIP() : gets its own IP address, adds it to the DNS record
# removeOldestEntry() : calls getPeerIP(), finds the oldest, and removes it using removeOldestEntry(record_num)
# removeIPRecord(record_num) : takes record number as param. Uses this number to delete DNS entry for that record.
# 

def getPeerIP():

    url = 'https://api.dnsimple.com/v1/domains/hashkittens.me/records'
    data = ""
    headers = {
        'X-DNSimple-Token': 'rjbaker@cmu.edu:jdAzT7XqRyF1GMKj7iVduHJFzlDCJkLS',
        'Accept': 'application/json'
        }
    r = requests.get(url, data=data, headers=headers)

    peerIP = []
    peerTimes = []
    peerRecordID = []
    peerCount = 0
    oldest = 0

    for i in r.json():
     dns_rec = str(i)
     if "'record_type': 'A'" in dns_rec:
      peerCount = peerCount + 1
      
      #get record number
      record_num = dns_rec[dns_rec.find("'id")+6:]
      record_num = record_num[:record_num.find(" ")-1]
      #print (record_num) 

      #get date/time
      time_index = dns_rec.find("'updated_at")+15
      time = dns_rec[ time_index : time_index + 19]
      #print (time)  

      #get IP address
      ip_addr = dns_rec[dns_rec.find("'content")+12 :]
      ip_addr = ip_addr[:ip_addr.find(" ")-2]
      #print (ip_addr)


      if peerCount is 1:
        peerTimes.append(time)
        peerIP.append(ip_addr)
        peerRecordID.append(record_num)
        
      else:
        t1 = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S")
        t2 = datetime.strptime(peerTimes[0], "%Y-%m-%dT%H:%M:%S")
        oldest = min((t1, t2))
        if oldest == t1:
           peerTimes.insert(0, time)
           peerIP.insert(0, ip_addr)
           peerRecordID.insert(0, record_num)

    return [peerIP, peerTimes, peerRecordID]

def postHostIP():
        
    #get public IP address
    url = 'http://ip.42.pl/raw'
    data = ""
    headers = ""
    r = requests.get(url, data=data, headers=headers)
    ip = str(r.text)
        
    #post to DNS record
    url = 'https://api.dnsimple.com/v1/domains/hashkittens.me/records'
    data = {
    'record': {
    'content': ip, 
    'record_type': 'A',
    'name': '', 
    'prio': 10, 
    'ttl': 3600}
    }
    headers = {
    'X-DNSimple-Token': 'rjbaker@cmu.edu:jdAzT7XqRyF1GMKj7iVduHJFzlDCJkLS',
    'Accept': 'application/json',
    'Content-Type' : 'application/json'
    }
    r = requests.post(url, data=json.dumps(data), headers=headers)
        
    return


def removeIPRecord(record_num):

    url = 'https://api.dnsimple.com/v1/domains/hashkittens.me/records/' + str(record_num)
    data = ""
    headers = {
    'X-DNSimple-Token': 'rjbaker@cmu.edu:jdAzT7XqRyF1GMKj7iVduHJFzlDCJkLS',
    'Accept': 'application/json',
    'Content-Type' : 'application/json'
    }
    r = requests.delete(url, data=data, headers=headers)

    return

def removeOldestIPEntry():

    #retrieve back lists of peers
    peerIP, peerTimes, peerRecordID = getPeerIP()

    #oldest record is in position 0 of the list
    removeIPRecord(peerRecordID[0])


def postPass2DNS(hash_string):
     #post to DNS record
    url = 'https://api.dnsimple.com/v1/domains/hashkittens.me/records'
    data = {
    'record': {
    'content': hash_string, 
    'record_type': 'TXT',
    'name': '', 
    'prio': 10, 
    'ttl': 3600}
    }
    headers = {
    'X-DNSimple-Token': 'rjbaker@cmu.edu:jdAzT7XqRyF1GMKj7iVduHJFzlDCJkLS',
    'Accept': 'application/json',
    'Content-Type' : 'application/json'
    }
    r = requests.post(url, data=json.dumps(data), headers=headers)
        
    return


