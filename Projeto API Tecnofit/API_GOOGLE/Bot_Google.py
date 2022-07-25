import pandas as pd
import os
from datetime import date
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = './chave_conta_servico.json'
VIEW_ID = '263629054'

def initialize_analyticsreporting():
  credentials = ServiceAccountCredentials.from_json_keyfile_name(
      KEY_FILE_LOCATION, SCOPES)
  analytics = build('analyticsreporting', 'v4', credentials=credentials)
  return analytics

#Get one report page
def get_report(analytics, pageTokenVar):
  return analytics.reports().batchGet(
      body={

##################################################################################

         'reportRequests': [
         {
           'viewId': VIEW_ID,
           'dateRanges': [{'startDate': '3daysAgo', 'endDate': 'yesterday'}],
           'metrics': [
               {'expression': 'ga:adClicks'},
               {'expression': 'ga:CPM'},
               {'expression': 'ga:CPC'},
               {'expression': 'ga:CTR'},
               {'expression': 'ga:RPC'},
               {'expression': 'ga:impressions'},
               {'expression': 'ga:adCost'},
               {'expression': 'ga:costPerTransaction'},
               {'expression': 'ga:costPerGoalConversion'},
               {'expression': 'ga:costPerConversion'}
           ],
           'dimensions': [
               {'name': 'ga:adwordsCampaignID'},
               {'name': 'ga:adGroup'}               
           ],
           'samplingLevel': 'LARGE',
           'pageSize': 10000
         }]

##################################################################################
          
      }
  ).execute()
    
def handle_report(analytics,pagetoken,rows):  
    response = get_report(analytics, pagetoken)

    #Header, Dimentions Headers, Metric Headers 
    columnHeader = response.get("reports")[0].get('columnHeader', {})
    dimensionHeaders = columnHeader.get('dimensions', [])
    metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])

    #Pagination
    pagetoken = response.get("reports")[0].get('nextPageToken', None)
    
    #Rows
    rowsNew = response.get("reports")[0].get('data', {}).get('rows', [])
    rows = rows + rowsNew
    print("len(rows): " + str(len(rows)))

    #Recursivly query next page
    if pagetoken != None:
        return handle_report(analytics,pagetoken,rows)
    else:
        #nicer results
        nicerows=[]
        for row in rows:
            dic={}
            dimensions = row.get('dimensions', [])
            dateRangeValues = row.get('metrics', [])

            for header, dimension in zip(dimensionHeaders, dimensions):
                dic[header] = dimension

            for i, values in enumerate(dateRangeValues):
                for metric, value in zip(metricHeaders, values.get('values')):
                    if ',' in value or ',' in value:
                        dic[metric.get('name')] = float(value)
                    else:
                        dic[metric.get('name')] = float(value)
            nicerows.append(dic)
        return nicerows



    
            
#Start
def main():    
    analytics = initialize_analyticsreporting()
    
    global dfanalytics
    dfanalytics = []

    rows = []
    rows = handle_report(analytics,'0',rows)
    data = date.today().strftime('%d-%m-%Y')
        
    caminho = os.path.dirname(__file__) + '\\arquivos\\' + data
    if not os.path.isdir(caminho):
        os.mkdir(caminho)
    
    dfanalytics = pd.DataFrame(list(rows))
    dfanalytics.to_csv(f'{caminho}\\tabela_resultado_google.csv',sep=';', quotechar='"', index=False)
    print('entrou')

if __name__ == '__main__':
  main()

dfanalytics