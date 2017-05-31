# rpcServer.py
import logging
import xmlrpclib, json, os, shutil, socket
import ConfigParser
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from product_downloader_util import download_data
from processor_start_util import run_processing
from datetime import datetime, timedelta


# store clients' IPs and Ports
monitor = {}


def init_stuff(log_file="processing.log"):
    """
    Init basic stuff
    :param log_file: the log file where logs need to be saved 
    """
    logging.basicConfig(filename=log_file,
                        filemode='a',
                        format='[CMEMS] %(asctime)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())
    # load server config properties
    logging.info("[CMEMS_RPC_SERVER] Initializing server instance")
    cp = ConfigParser.ConfigParser()
    cp.read("serverConfig.ini")
    serverConf = dict(cp.items('server'))
    server = SimpleXMLRPCServer((serverConf["host"], int(serverConf["port"]) ), customXMLRPCHandler)
    logging.info("[CMEMS_RPC_SERVER] Done initializing server instance")
    return server

# !!! **** ADD Processors dir to PYTHONPATH **** !!!!      

class customXMLRPCHandler(SimpleXMLRPCRequestHandler):
    def do_POST(self):
        global monitor
        monitor["clientIP"], monitor["clientPort"] = self.client_address
        SimpleXMLRPCRequestHandler.do_POST(self)

# 
def execute(jsonData):
    logging.info("---------------------------------------------------------------------")
    logging.info("[CMEMS_RPC_SERVER] Got new request")
    # parse json to dictionary
    argsDict = json.loads(jsonData)
    
    try:
        def_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        download_data(argsDict.get('date', def_date), argsDict.get('date', def_date))
        rslt = run_processing(argsDict.get('products', 3), argsDict.get('overwrite', 3))
        logging.info("[CMEMS_RPC_SERVER] Result dict: %s" %rslt)
    except Exception as e:
        logging.error("[CMEMS_RPC_SERVER] Error in processing data")
        logging.exception(e)
        return json.dumps({"status":"e"})
    
    logging.info("[CMEMS_RPC_SERVER] Request served")
    logging.info("---------------------------------------------------------------------")
    return json.dumps({"s": rslt})



server = init_stuff()

server.register_instance(monitor)
server.register_function(execute, "execute")
server.serve_forever()
