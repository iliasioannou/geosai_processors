from datetime import datetime, timedelta
import logging

from product_downloader.downloader.downloader import run_script
from product_downloader.script.script import StringScriptBuilder

data_map = [
    # {
    #     "product": "MEDSEA_ANALYSIS_FORECAST_BIO_006_014",
    #     "base_url": "http://cmems-med-mfc.eu/motu-web/Motu",
    #     "dataset": [
    #         {
    #             # Dissolved Oxygen
    #             "name": "",
    #             "values": [
    #                 ""
    #             ]
    #         }
    #     ]
    # },
    {
        "product": "MEDSEA_ANALYSIS_FORECAST_PHY_006_013",
        "base_url": "http://cmems-med-mfc.eu/motu-web/Motu",
        "dataset": [
            {
                # Sea Surface Temperature
                "name": "sv03-med-ingv-tem-an-fc-d",
                "values": [
                    "Tethao",
                    "bottomT"
                ]
            },
            {
                # Salinity
                "name": "sv03-med-ingv-sal-an-fc-d",
                "values": [
                    "so"
                ]
            },
            {
                # Currents
                "name": "sv03-med-ingv-cur-an-fc-d",
                "values": [
                    "uo",
                    "vo"
                ]
            }
        ]
    }
    # ,
    # {
    #     # Sea Surface Waves
    #     "product": "MEDSEA_ANALYSIS_FORECAST_WAV_006_011",
    #     "base_url": "http://cmems-med-mfc.eu/motu-web/Motu",
    #     "dataset": [
    #         {   
    #             "name": "",
    #             "values": [
    #                 ""
    #             ]
    #         }
    #     ]
    # }
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
            if not result:
                logging.info("[EOSAI_DOWNLOADER] %s (%s) Not completed" %(ds['name'], start_date))
            else:
                logging.info("[EOSAI_DOWNLOADER] %s (%s) Completed" %(ds['name'], start_date))
        logging.info("[EOSAI_DOWNLOADER] Finished downloading product")
