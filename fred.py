import requests
import pandas as pd

#899901ba06f09b9961a73113b1834a15

class Fred_Pull:

    def __init__(self,series_id,api_key):
        
        self.series_id = series_id
        self.api_key = api_key

    def fetch(self):
        
        root = 'https://api.stlouisfed.org/fred/series/observations'
        params = {
            'series_id': self.series_id,
            'api_key': self.api_key,
            'file_type': 'json'
        }

        return requests.get(root, params=params)

    def extract(self,month_average=False):

        if self.fetch().json()['observations']:
            df = (
                pd.DataFrame(self.fetch().json()['observations'])
                .drop(columns=['realtime_start', 'realtime_end'])
                .assign(
                    date=lambda df: pd.to_datetime(df['date']),
                    value=lambda df: pd.to_numeric(df['value'],errors='coerce')
                )
                .set_index('date')
                .rename(columns={'value':self.series_id})
            )

        else:
            print('Ticker does not exist')

        if month_average:
            return df.resample('ME').mean()
        else:
            return df

    def index(self,start,month_average=False):
        df = self.extract(month_average)
        return (
            df[df.index.year>=start]
            .apply(lambda x: 1/(x/x.iloc[0]))
        )
