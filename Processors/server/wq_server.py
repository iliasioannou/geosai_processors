# rpcServer.py
import xmlrpclib, json, os, shutil, socket
import ConfigParser
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from product_downloader_util import download_data

# store clients' IPs and Ports
monitor = {}

# save original working directory
startPath = os.getcwd()

# load server config properties
cp = ConfigParser.ConfigParser()
cp.read("serverConfig.ini")
serverConf = dict(cp.items('server'))
print "Server configuration loaded."

# !!! **** ADD Processors dir to PYTHONPATH **** !!!!      

class customXMLRPCHandler(SimpleXMLRPCRequestHandler):
    def do_POST(self):
        global monitor
        monitor["clientIP"], monitor["clientPort"] = self.client_address
        SimpleXMLRPCRequestHandler.do_POST(self)

# 
def execute(productID, scriptName, jsonData):
    
    # parse json to dictionary
    argsDict = json.loads(jsonData)
    print "\n -------------*** SERVER: received new request! ***--------------- \nPayload:"
    print argsDict
    
    # import requested module 
    print "SERVER: Importing module named " + scriptName
    module = __import__(productID+'.'+scriptName)
    proc = module.__dict__[scriptName]

    # load an inject config properties
    config = ConfigParser.ConfigParser()
    config.read(module.__path__[0]+"\\config.ini")
    configDict = dict(config.items(scriptName))
    print "SERVER: Loaded config: " + str(configDict)
    proc.__dict__.update( configDict )
    
    print proc
    print dir(proc)

    print "SERVER: call run() from imported module"
    print "- MODULE STDOUT -\n"
    download_data()
    outDict = proc.run(argsDict)

    print "\n- END MODULE STDOUT -"

    
    print "SERVER: sending back module run() output"
    print outDict
    
    print "MONITOR:",monitor["clientIP"]

    # Restore original working directory
    os.chdir(startPath)
    
    return json.dumps(outDict)

server = SimpleXMLRPCServer((serverConf["host"], int(serverConf["port"]) ), customXMLRPCHandler)
print "Listening on port "+serverConf["port"]

server.register_instance(monitor)

server.register_function(execute, "execute")
server.serve_forever()
