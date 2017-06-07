from datetime import datetime, timedelta
import logging

from product_downloader.downloader.downloader import Runner
from product_downloader.script.script import StringScriptBuilder

data_map = [
    {
        "product": "OCEANCOLOUR_MED_OPTICS_L3_NRT_OBSERVATIONS_009_038-TDS",
        "base_url": "http://cmems-oc.isac.cnr.it/motu-web/Motu",
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
        "base_url": "http://cmems-oc.isac.cnr.it/motu-web/Motu",
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
        "base_url": "http://cmems.isac.cnr.it/mis-gateway-servlet/Motu",
        "dataset": [
            {   
                "name": "SST_MED_SST_L3S_NRT_OBSERVATIONS_010_012_b",
                "values": [
                    "sea_surface_temperature",
                    "source_of_sst",
                    "quality_level",
                    "adjusted_sea_surface_temperature"
                ]
            }
        ]
    },
    # {
    #     "product": "OCEANCOLOUR_MED_OPTICS_L3_REP_OBSERVATIONS_009_095-TDS",
    #     "base_url": "http://cmems-oc.isac.cnr.it/motu-web/Motu",
    #     "dataset": [
    #         {
    #             "name": "dataset-oc-med-opt-multi_cci-l3-rrs490_1km_daily-rep-v02",
    #             "values": [
    #                 "RRS490"
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
    logging.info("[CMEMS_DOWNLOADER] Start downloading product")
    downloader = Runner()

    for element in data_map:
        logging.info("[CMEMS_DOWNLOADER] Processing %s" %element['product'])
        for ds in element['dataset']:
            logging.info("[CMEMS_DOWNLOADER] Downloading %s" % ds['name'])
            script = StringScriptBuilder()\
                .set_product(element['product'])\
                .set_dataset(ds['name'])\
                .set_values(ds['values'])\
                .set_dates([start_date, end_date])\
                .set_base_url(element['base_url'])\
                .set_out_name("%s_%s.nc" %(ds['name'], start_date))\
                .build()
            result = downloader.run_script(script, assert_result_function=lambda item: True if "Done" in item[0] and item[1].returncode == 0 else False)
            if not result:
                logging.info("[CMEMS_DOWNLOADER] %s (%s) Not completed" %(ds['name'], start_date))
            else:
                logging.info("[CMEMS_DOWNLOADER] %s (%s) Completed" %(ds['name'], start_date))
        logging.info("[CMEMS_DOWNLOADER] Finished downloading product")
