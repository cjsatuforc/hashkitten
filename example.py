#!/usr/bin/env python
from bootstrapping import getPeerIP, postHostIP, removeOldestIPEntry, removeIPRecord

peerIP, peerTimes, peerRecordID = getPeerIP()

print (peerIP)
print (peerTimes)
print (peerRecordID)

#To Remove Oldest IP Address
#removeOldestIPEntry()

#To Add current Host
#postHostIP()

peerIP, peerTimes, peerRecordID = getPeerIP()

print (peerIP)
print (peerTimes)
print (peerRecordID)
