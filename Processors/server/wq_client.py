# client.py
import xmlrpclib
import json


proxy = xmlrpclib.ServerProxy("http://localhost:9091/")
print "Calling the server processor ..."

procOut = proxy.execute(json.dumps({"date":"2017-05-30"}))

print procOut

print "Press Enter to exit"
