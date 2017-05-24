# client.py
import xmlrpclib

proxy = xmlrpclib.ServerProxy("http://localhost:9091/")
print "Calling the server processor ..."

procOut = proxy.execute("water_quality_modis_twq", "processor", '{ "twq": "{}", "date": "201666666"}')

print procOut

print "Press Enter to exit"
raw_input()
