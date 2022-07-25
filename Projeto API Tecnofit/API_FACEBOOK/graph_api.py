import requests
import json
import pandas as pd
import os
from datetime import date



class GraphAPI:
    def __init__(self, fb_api): 
        self.base_url = 'https://graph.facebook.com/v13.0/'
        self.api_fields = ['account_name','campaign_name', 'buying_type', 'reach','spend','purchase_roas', 'cpp','cpm','impressions','cost_per_action_type','cost_per_conversion','inline_link_click_ctr', 'inline_link_clicks','cost_per_inline_link_click','actions']
        self.token = "&access_token=" + fb_api
        self.data = date.today().strftime('%d-%m-%Y')
        self.caminho = os.path.dirname(__file__) + '\\arquivos\\' + self.data
        
    def cria_diretorio(self, caminho):
        if not os.path.isdir(caminho):
            os.mkdir(caminho)
    
    def get_id_account(self):
        r = requests.get("https://graph.facebook.com/v13.0/me?fields=adaccounts%7Bname%7D" + self.token)
        data = json.loads(r._content.decode('utf-8'))
        lista = []
        for key in data['adaccounts']['data']:
            lista.append({'name':key['name'], 'id':key['id']})
            
        return lista
        
    def get_insights(self, level="campaign"):
        for act in self.get_id_account():
            url = self.base_url + act['id']
            url += '/insights?level=' + level
            url += '&fields=' + ','.join(self.api_fields)
            
            data_request = requests.get(url +'&date_preset=yesterday' +  self.token)
            if (data_request.status_code==200):
                print("entrou")
                data_json = json.loads(data_request._content.decode('utf8'))            
                df = pd.json_normalize(data_json['data'])
                self.cria_diretorio(self.caminho)
                if (df.size>0):
                    #df.to_excel(f'{self.caminho}\\tabela_resultado_facebook - {act["name"]}.xlsx', index=False)
                    df.to_json(f'{self.caminho}\\tabela_resultado_facebook - {act["name"]}.json', force_ascii=False)
        
if __name__ == "__main__":
    fb_api = open("tokens/fb_token").read()
    GraphAPI(fb_api).get_insights()
    