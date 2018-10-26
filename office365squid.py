#!/usr/bin/env python2.7
# -*- coding: utf-8 -*
import requests,re,os,json
import datetime
import xml.etree.ElementTree as ET
from shutil import copyfile



Office365URL = "https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7"
Squidconf = "/etc/squid/office365.conf"

## Funct
#

def getOfficeURL(URL):
  Office365Data = requests.get(URL).text.decode("utf-8")
  Office365json = json.loads(Office365Data)
  Office365URLList = []
  for item in Office365json:
    #print ("# {0} -> {1}".format((item[u'id']),item[u'serviceAreaDisplayName']))
    if (u'urls' in item.keys()):
      #print (item['urls'])
      Office365URLList = Office365URLList + item[u'urls']
  return Office365URLList

def getCleanList(URLList):
  OutList = []
  for address in URLList:
        URL =  address
        #print ("Procesing   : {0}".format(URL))
        # Remove asterisk
        URL = re.sub('\*','',URL)
        # Remove two points
        URL = re.sub('\.\.\.*','\.',URL)
        OutList.append(URL)
        #tempFile.write (URL + "\n")
  return OutList

def indomains(seq):
  out = []
  for item in seq:
    match = False
    for item2 in seq:
      if (((re.search(item2,item)) or (("." + item) == item2)) and (item2 != item)):
        #print ("  Item {0} match Item2 => {1}".format(item,item2))
        match = True
        break
    if (match == False):
      out.append(item)
      #print ("Item added: {0} ".format(item))
  return out
  
  
  
# Enabled the log
import logging,sys,tempfile
logfile = "/var/log/office365squid.log"
logging.basicConfig(filename=logfile,level=logging.DEBUG, format=' %(asctime)s - %(levelname)s- %(message)s')
logging.debug("## Runing " + sys.argv[0] + " ..")
# tempfile
tempPath = tempfile.NamedTemporaryFile()
logging.debug('Tmp filename: %s' % tempPath.name)
logging.debug('Office365 URL: %s' % Office365URL)
tempFile = open(tempPath.name,'wb')


# Some info
CurrentDate = datetime.datetime.now()
tempFile.write ("## Squid file for Office365 \n")
tempFile.write ("# Generated at: %s\n" % CurrentDate)
tempFile.write ("# Removed '*', ',' and multiple '.' \n")
tempFile.write ("\n")
logging.debug("Current date: {0}".format(CurrentDate))

DomainLists = getOfficeURL(Office365URL)
# Remove rare char
DomainLists = getCleanList(DomainLists)
logging.debug("Elements Number : {0}".format(len(DomainLists)))
# Remove dups
DomainLists = list(set(DomainLists))
logging.debug("Elements Number after remove duplicates : {0}".format(len(DomainLists)))
# Remote duplicates
DomainLists = indomains(DomainLists)
logging.debug("Elements Number after remove child Domains : {0}".format(len(DomainLists)))

# Order file
import locale
locale.setlocale(locale.LC_ALL, '')
DomainLists.sort(cmp=locale.strcoll)
   
# send to file
for item in DomainLists:
        tempFile.write ("%s\n" % item)
tempFile.close()

# Before copy
TmpfileSize = (os.stat(tempPath.name).st_size)
try:
  SquifFileSize = (os.stat(Squidconf).st_size)
except:
  SquifFileSize = 0
  logging.debug("Dest file not exits: {0}".format(Squidconf))

logging.debug("New file size: {0}".format(TmpfileSize))
logging.debug("Current file size: {0}".format(SquifFileSize))

if (TmpfileSize == SquifFileSize):
  logging.debug("Same size, not overwrite")
else:
    if (TmpfileSize < 501):
      logging.debug("May be empty file, not overwrite")
    else:
      copyfile(tempPath.name, Squidconf)
      logging.debug("The file {0} was replaced!!!".format(Squidconf))

logging.debug("Run end.")
