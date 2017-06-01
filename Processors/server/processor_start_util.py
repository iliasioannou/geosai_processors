from processors.C2_Scripting.pkz029_WQ_CMEMS_Processor import WQ_CMEMS_Chain
import logging
from datetime import datetime

def run_processing(products, overwrites, date=datetime.now().strftime("%Y-%m-%d")):
    #if len(sys.argv)!=4:
    #    raise Exception("Wrong number of arguments!") 
    #param1=int(sys.argv[1])
    #param2=int(sys.argv[2])
    #IDS=sys.argv[3]

    logging.info("[CMES_PROCESSORS] Starting processing data")
    res=WQ_CMEMS_Chain(products, overwrites,date)
    logging.info("[CMES_PROCESSORS] End processing data")
    return res
    # lg=open(output_dir+IDS+'_log.txt','w')
    # for linea in ErrorMessage:
    #     lg.write(linea+'\n')
    # lg.close()