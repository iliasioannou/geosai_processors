from processors.Scripting.pkz029_WQ_CMEMS_Processor import WQ_CMEMS_Chain
import logging

def run_processing(products, overwrites):
    #if len(sys.argv)!=4:
    #    raise Exception("Wrong number of arguments!") 
    #param1=int(sys.argv[1])
    #param2=int(sys.argv[2])
    #IDS=sys.argv[3]

    logging.info("[CMES_PROCESSORS] Starting processing data")
    res=WQ_CMEMS_Chain(products, overwrites,3)
    logging.info("[CMES_PROCESSORS] End processing data")
    return res
    # lg=open(output_dir+IDS+'_log.txt','w')
    # for linea in ErrorMessage:
    #     lg.write(linea+'\n')
    # lg.close()