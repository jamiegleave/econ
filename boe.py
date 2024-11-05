import pandas as pd
import requests
import io
from datetime import datetime as dt

class boe_pull:

    def __init__(self,series_id):
        
        self.series_id = series_id

    def fetch(self):
        
        url_endpoint = 'http://www.bankofengland.co.uk/boeapps/iadb/fromshowcolumns.asp?csv.x=yes'

        payload = {
            'Datefrom'   : '01/Jan/1995',
            'Dateto'     : dt.today().strftime("%d/%b/%Y"),
            'SeriesCodes': self.series_id,
            'CSVF'       : 'TN',
            'UsingCodes' : 'Y',
            'VPD'        : 'Y',
            'VFD'        : 'N'
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                        'AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/54.0.2840.90 '
                        'Safari/537.36'
        }

        return requests.get(url_endpoint, params=payload, headers=headers)


    def extract(self):

        return pd.read_csv(io.BytesIO(self.fetch().content)).set_index('DATE')