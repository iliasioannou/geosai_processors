# client.py
import xmlrpclib
import json
from datetime import datetime, timedelta

proxy = xmlrpclib.ServerProxy("http://localhost:9091/")
print "Calling the server processor ..."


for i in range(2, 30):
    data = dict(
        gte=(datetime.now() + timedelta(days=-i)).strftime("%Y-%m-%d")
    )
    print("Processing ", data)
    proxy.execute(json.dumps(data))

print "Press Enter to exit"
