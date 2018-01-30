# rpcServer.py
import logging
import xmlrpclib, json, os, shutil, socket
import ConfigParser
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from product_downloader_util import download_data
from processor_util import run_processing
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
                        format='[EOSAI] %(asctime)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())
    # load server config properties
    logging.info("[EOSAI_RPC_SERVER] Initializing server instance")
    cp = ConfigParser.ConfigParser()
    cp.read("serverConfig.ini")
    serverConf = dict(cp.items('server'))
    server = SimpleXMLRPCServer((serverConf["host"], int(serverConf["port"])), customXMLRPCHandler)
    logging.info("[EOSAI_RPC_SERVER] Done initializing server instance")
    return server


# !!! **** ADD Processors dir to PYTHONPATH **** !!!!

class customXMLRPCHandler(SimpleXMLRPCRequestHandler):
    def do_POST(self):
        global monitor
        monitor["clientIP"], monitor["clientPort"] = self.client_address
        SimpleXMLRPCRequestHandler.do_POST(self)


def execute(data):
    logging.info("---------------------------------------------------------------------")
    logging.info("[EOSAI_RPC_SERVER] Got new request")
    # parse json to dictionary
    argsDict = json.loads(data)
    try:
        def_date = (datetime.now()).strftime("%Y-%m-%d")
        if 'runDate' in argsDict:
            gte_date = argsDict['runDate']
        else:
            gte_date = argsDict.get('gte', def_date) if "gte" in argsDict else def_date
        # lte_date = argsDict.get('lte', def_date) if "lte" in argsDict else def_date
        if argsDict.get('procType', 'day') == 'day':
            download_data(gte_date, gte_date)

        logging.info("[EOSAI_RPC_SERVER] Got params: %s" %data)
        rslt = run_processing(
            processing_type=argsDict.get('procType', 'day'),
            products=int(argsDict.get('products', 31)),
            overwrites=int(argsDict.get('overwrite', 31)),
            setAoi=int(argsDict.get('aoi', 3)),
            final_folder="/src/Processors/server/processors/C5_OutputDir",
            yes_no_folder="/src/Processors/server/processors/C4_TempDir",
            date=gte_date if not "dates" in argsDict else argsDict['dates']
        )
        logging.info("[EOSAI_RPC_SERVER] Result dict: %s" % rslt)
        #logging.info("[EOSAI_RPC_SERVER] Out path : %s" % out_path)
    except Exception as e:
        logging.error("[EOSAI_RPC_SERVER] Error in processing data")
        logging.exception(e)
        return json.dumps({"returnCode": 1, "message": str(e)})

    logging.info("[EOSAI_RPC_SERVER] Request served")
    logging.info("---------------------------------------------------------------------")
    return json.dumps({"returnCode": rslt, "outPath": "geoserver/data/eosai/raster/"})


server = init_stuff()

server.register_instance(monitor)
server.register_function(execute, "execute")
server.serve_forever()
