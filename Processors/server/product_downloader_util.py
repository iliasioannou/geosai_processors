from datetime import datetime, timedelta
import logging

from Processors.server.product_downloader.downloader.downloader import Downloader
from Processors.server.product_downloader.script.script import StringScriptBuilder

data_map = [
    {
        "product": "OCEANCOLOUR_MED_OPTICS_L3_NRT_OBSERVATIONS_009_038-TDS",
        "dataset": [
            {
                "name": "dataset-oc-med-opt-multi-l3-kd490_1km_daily-rt-v02",
                "values": [
                    "SENSORMASK",
                    "KD490",
                    "QI"
                ]
            },
            {
                "name": "dataset-oc-med-opt-multi-l3-rrs490_1km_daily-rt-v02",
                "values": [
                    "SENSORMASK",
                    "RRS490",
                    "QI"
                ]
            },
            {
                "name": "dataset-oc-med-opt-multi-l3-rrs555_1km_daily-rt-v02",
                "values": [
                    "SENSORMASK",
                    "RRS555",
                    "QI"
                ]
            },
            {
                "name": "dataset-oc-med-opt-multi-l3-rrs670_1km_daily-rt-v02",
                "values": [
                    "SENSORMASK",
                    "RRS670",
                    "QI"
                ]
            }
        ]
    },
    {
        "product": "OCEANCOLOUR_MED_CHL_L3_NRT_OBSERVATIONS_009_040-TDS",
        "dataset": [{
            "name": "dataset-oc-med-chl-multi-l3-chl_1km_daily-rt-v02",
            "values": [
                "WTM",
                "CHL",
                "SENSORMASK",
                "QI"
            ]
        }
        ]
    },
    {
        "product": "SST_MED_SST_L3S_NRT_OBSERVATIONS_010_012-TDS",
        "dataset": [
            {
                "name": "SST_MED_SST_L3S_NRT_OBSERVATIONS_010_012_a",
                "values": [
                    "sea_surface_temperature",
                    "source_of_sst",
                    "quality_level",
                    "adjusted_sea_surface_temperature"
                ]
            }
        ]
    },
    {
        "product": "OCEANCOLOUR_MED_OPTICS_L3_REP_OBSERVATIONS_009_095-TDS",
        "dataset": [
            {
                "name": "dataset-oc-med-opt-multi_cci-l3-rrs490_1km_daily-rep-v02",
                "values": [
                    "RRS490"
                ]
            }
        ]
    }
]


def init_log(log_file="processing.log"):
    """
    Init logger
    :param log_file: the log file where logs need to be saved 
    """
    logging.basicConfig(filename=log_file,
                        filemode='a',
                        format='[CMEMS_DOWNLOADER] %(asctime)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)


def download_data():
    """
    Run the download process
    Iterate over the data_map structure and and start downloading products.
    """
    init_log()

    logging.info("Start downloading product")
    downloader = Downloader()

    for element in data_map:
        logging.info("[CMEMS_DOWNLOADER] Processing %s" %element['product'])
        for ds in element['dataset']:
            dates = [(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")]*2
            logging.info("[CMEMS_DOWNLOADER] Downloading %s" % ds['name'])
            script = StringScriptBuilder()\
                .set_product(element['product'])\
                .set_dataset(ds['name'])\
                .set_values(ds['values'])\
                .set_dates(dates)\
                .set_out_name("%s_%s.nc" %(ds['name'], dates[0]))\
                .build()
            result = downloader.download(script)
            if not result:
                logging.info("[CMEMS_DOWNLOADER] %s (%s) Not completed" %(ds['name'], dates[0]))
            else:
                logging.info("[CMEMS_DOWNLOADER] %s (%s) Completed" %(ds['name'], dates[0]))
        logging.info("[CMEMS_DOWNLOADER] Finished downloading product")
