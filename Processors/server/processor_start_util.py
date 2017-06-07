from processors.C2_Scripting.pkz029_WQ_CMEMS_Processor import WQ_CMEMS_Chain
import logging
from datetime import datetime

def run_processing(products, overwrites, date=datetime.now().strftime("%Y-%m-%d")):
    """
    Run processing calling processors

    products: the products that need to be generated
    overwrites: overwrite or not previous result
    date: the date whose products belongs to
    """
    logging.info("[CMES_PROCESSORS] Starting processing data")
    res=WQ_CMEMS_Chain(products, overwrites,date)
    logging.info("[CMES_PROCESSORS] End processing data")
    return res
    