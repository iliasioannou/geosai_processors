from datetime import datetime, timedelta
import logging

from product_downloader.downloader.downloader import run_script
from product_downloader.script.script import StringScriptBuilder

data_map = [
    {
        "product": "MEDSEA_ANALYSIS_FORECAST_BIO_006_014",
        "base_url": "http://cmems-med-mfc.eu/motu-web/Motu",
        "dataset": [
            {
                # Dissolved Oxygen  [mmol O2/m3]
                "name": "sv03-med-ogs-bio-an-fc-d",
                "values": [
                    "dox"
                ]
            }
        ]
    },
    {
        "product": "MEDSEA_ANALYSIS_FORECAST_PHY_006_013",
        "base_url": "http://cmems-med-mfc.eu/motu-web/Motu",
        "dataset": [
            {
                # Sea Surface Temperature [degC]
                "name": "sv03-med-ingv-tem-an-fc-d",
                "values": [
                    "Tethao"
                ]
            },
            {
                # Salinity [1e-3]
                "name": "sv03-med-ingv-sal-an-fc-d",
                "values": [
                    "so"
                ]
            },
            {
                # Currents [m/s]
                "name": "sv03-med-ingv-cur-an-fc-d",
                "values": [
                    "uo",
                    "vo"
                ]
            }
        ]
    },
    {
        "product": "MEDSEA_ANALYSIS_FORECAST_WAV_006_011",
        "base_url": "http://cmems-med-mfc.eu/motu-web/Motu",
        "dataset": [
            {   
                # Sea Surface Waves [m]
                "name": "sv03-med-hcmr-wav-an-fc-h",
                "values": [
                    "VHM0"
                ]
            }
        ]
    }
]


def download_data(start_date, end_date):
    """
    Run the download process
    Iterate over the data_map structure and and start downloading products.
    
    :param startDate: the start date whose products need to be downloaded from
    :param endDate: the end date whose products need to be downloaded to
    """
    logging.info("[EOSAI_DOWNLOADER] Start downloading product")

    for element in data_map:
        logging.info("[EOSAI_DOWNLOADER] Processing %s" %element['product'])
        for ds in element['dataset']:
            logging.info("[EOSAI_DOWNLOADER] Downloading %s" % ds['name'])
            script = StringScriptBuilder()\
                .set_product(element['product'])\
                .set_dataset(ds['name'])\
                .set_values(ds['values'])\
                .set_dates([start_date, end_date])\
                .set_base_url(element['base_url'])\
                .set_out_name("%s_%s.nc" %(ds['name'], start_date))\
                .build()
            result = run_script(script, assert_result_function=lambda item: True if "Done" in item[0] and item[1].returncode == 0 else False)
            logging.info("[EOSAI_DOWNLOADER] REQUEST SCRIPT: %s " %(script))
            if not result:
                logging.info("[EOSAI_DOWNLOADER] %s (%s) Not completed" %(ds['name'], start_date))
            else:
                logging.info("[EOSAI_DOWNLOADER] %s (%s) Completed" %(ds['name'], start_date))
        logging.info("[EOSAI_DOWNLOADER] Finished downloading product(s)")
