from processors.C2_Scripting.pkz029_WQ_CMEMS_OnDemandStatistics import WQ_OnDemandStats_CMEMS_Chain
from processors.C2_Scripting.pkz029_WQ_CMEMS_Processor import WQ_CMEMS_Chain
from processors.C2_Scripting.pkz029_WQ_CMEMS_Statistics import WQ_Stats_CMEMS_Chain
import logging
from datetime import datetime



def run_processing(products, overwrites, processing_type, date=datetime.now().strftime("%Y-%m-%d")):
    """
    Run processing calling processors

    :param products: the products that need to be generated
    :param overwrites: overwrite or not previous result
    :param processing_type: the type of the processing to be launched.
    :param date: the date whose products belongs to
    """
    processor_entrypoint = {
        'day': WQ_CMEMS_Chain,
        'ten': WQ_Stats_CMEMS_Chain,
        'month': WQ_Stats_CMEMS_Chain,
        'custom': WQ_OnDemandStats_CMEMS_Chain
    }
    logging.info("[CMES_PROCESSORS] Starting processing data")
    res=processor_entrypoint[processing_type](products, overwrites, date)
    logging.info("[CMES_PROCESSORS] End processing data")
    return res