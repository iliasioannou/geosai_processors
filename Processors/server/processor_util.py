from processors.C2_Scripting.pkh111_WQ_EOSAI_OnDemandStatistics import WQ_OnDemandStats_EOSAI_Chain
from processors.C2_Scripting.pkh111_WQ_EOSAI_Processor import WQ_EOSAI_Chain
from processors.C2_Scripting.pkh111_WQ_EOSAI_Statistics import WQ_Stats_EOSAI_Chain
import logging
from datetime import datetime

def run_processing(products, overwrites, processing_type, setAoi, date=datetime.now().strftime("%Y-%m-%d")):
    """
    Run processing calling processors

    :param products: the products that need to be generated
    :param overwrites: overwrite or not previous result
    :param processing_type: the type of the processing to be launched.
    :param date: the date whose products belongs to
    """
    processor_entrypoint = {
        'day': WQ_EOSAI_Chain,
        'ten': WQ_Stats_EOSAI_Chain,
        'month': WQ_Stats_EOSAI_Chain,
        'custom': WQ_OnDemandStats_EOSAI_Chain
    }
    logging.info("[EOSAI_PROCESSORS] Starting processing data")
    res=processor_entrypoint[processing_type](products, overwrites, date)
    logging.info("[EOSAI_PROCESSORS] End processing data")
    return res