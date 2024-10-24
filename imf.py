import requests
import pandas as pd
from time import sleep

class IMF_Pull:

    def __init__(self,dataset,country,indicators):
        
        self.dataset = dataset
        self.country = country
        self.indicators = indicators

    def fetch(self,indicator):
        base_url = 'http://dataservices.imf.org/REST/SDMX_JSON.svc'

        query_url = f"{base_url}/CompactData/{self.dataset}/A.{self.country}.{indicator}"

        response = requests.get(query_url)
        return response.json()      #limited due to IMF cooldown policy...

    def parse_response(self,json_data):
        
        series_data = []
        name = json_data.get('CompactData').get('DataSet').get('Series').get('@INDICATOR')

        for obs in json_data.get("CompactData").get("DataSet").get("Series").get("Obs"):
            series_data.append({
                "Date": obs.get("@TIME_PERIOD"),
                name: pd.to_numeric(obs.get("@OBS_VALUE")),
                })
        
        return series_data

    def extract(self):
        
        if type(self.indicators)==str:
            return self.parse_response(self.fetch(self.indicators))

        if type(self.indicators)==list:
            df = pd.DataFrame()

            for i in self.indicators:
                df = pd.concat([df,
                                pd.DataFrame(self.parse_response(self.fetch(i)))
                                .set_index('Date')],axis=1)
                sleep(2)
                
            return df


            #for i in self.indicators:
                #result[i] = self.fetch(i)
                #result[i] = self.parse_response(self.fetch(i))
            
            #for j in sorted(result.values(),key=lambda x:len(x),reverse=True):
                #df = pd.concat([df,pd.DataFrame.from_dict(j).set_index('Date')],axis=1)