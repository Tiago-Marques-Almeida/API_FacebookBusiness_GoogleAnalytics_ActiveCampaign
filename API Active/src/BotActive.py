from ntpath import join
import os
import shutil
import time
from datetime import datetime, timedelta
import configActive
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotInteractableException


class Bot():

    def __init__(self):
        self.reset_ambiente()
        self.driver = self.get_driver()
        self.dia_anterior_contratos = (datetime.now() - timedelta (1)).strftime('%d/%m/%Y')
        self.dia_anterior = (datetime.now() - timedelta (1)).strftime('%d-%m-%Y') 
        self.proximo_mes = (datetime.now() + timedelta (30)).strftime('%d/%m/%Y') 
        self.data= datetime.today().strftime('%d-%m-%Y')               
        self.run()
   
    def get_driver(self):
        chrome_options = Options()
        #chrome_options.add_argument('--headless')
        chrome_options.add_experimental_option("prefs", {"download.default_directory": configActive.DIRETORIO_ARQUIVOS_TEMP})
        s=Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=s,options=chrome_options)
        driver.maximize_window()
        return driver


    def cria_diretorio(self, caminho):
        if not os.path.isdir(caminho):
            os.mkdir(caminho)


    def reset_ambiente(self):
        list_caminhos = [
            configActive.DIRETORIO_ARQUIVOS_TEMP
                   ]
        for caminho in list_caminhos:
            if os.path.isdir(caminho):
                shutil.rmtree(caminho)
            self.cria_diretorio(caminho)


    def login(self, usuario, senha):
        self.driver.get(configActive.URL_SISTEMA)
        self.retorna_elemento('ID', 'user').send_keys(usuario)
        time.sleep(1)
        self.retorna_elemento('ID', 'pass').send_keys(senha)
        time.sleep(1)
        self.retorna_elemento('XPATH','//*[@id="log_user"]/div[3]/input').click()
        #tempo necessário pois o carregamento do site demora
        time.sleep(3)
        

    def aguarda_download(self):
        seconds = 1
        dl_wait = True
        while dl_wait and seconds < 60:
            time.sleep(2)
            dl_wait = False
            for fname in os.listdir(configActive.DIRETORIO_ARQUIVOS_TEMP):
                if fname.endswith('.crdownload'):
                    dl_wait = True
            seconds += 1
        return seconds

    def renomar_arquivo(self, original, alterar):
        self.aguarda_download()
        #os.rename(original, alterar)
        shutil.move(original, alterar)
        
    
    def cria_diretorio(self, caminho):
        if not os.path.isdir(caminho):
            os.mkdir(caminho)

    
    def retorna_elemento(self, funcao, path):
        self.aguardar_elemento(funcao, path)
        return self.driver.find_element(getattr(By,funcao), path)


    def aguardar_elemento(self, funcao, path):
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((getattr(By,funcao), path)))
   
    
    def baixa_relatorio_performance(self):
        #abre página onde está o relatório de performance
        self.driver.get('https://academiaevolve.activehosted.com/app/reports/campaigns/performance')
        time.sleep(5)
        #clica para abrir o leque de opções de data
        self.retorna_elemento('CLASS_NAME', 'caret').click()
        #seleciona o dia de ontem
        self.retorna_elemento('XPATH','//*[@id="filter-campaign-date"]/div/ul/li[2]/a').click()
        time.sleep(120)
        #mudando de iframe
        iframe = self.retorna_elemento('XPATH', '//*[@id="ember668"]/iframe')
        self.driver.switch_to.frame(iframe)

        #teste se existe tabela a ser baixado
        
        if (len(self.driver.find_elements(By.XPATH, "//span[@class='column-label']"))>0):
            print('Baixando relatório')
            #move o mouse até  um local que apareça os 3 pontinhos
            element_to_hover_over = self.retorna_elemento('XPATH', "//span[@class='column-label']")
            hover = ActionChains(self.driver).move_to_element(element_to_hover_over)
            hover.perform()
            #clica nos 3 pontinhos que apareceu
            self.retorna_elemento('XPATH', '//*[@id="dashboard"]/div/div[2]/div/div/div/div/div/lk-vis-element/div/div/div[5]/div/div/span').click()
            time.sleep(3)
            #clica em baixar arquivo que aparece depois
            self.retorna_elemento('XPATH', '//*[@id="lk-layout-embed"]/ul/li[1]/a').click()
            time.sleep(30)

            #seleciona excel
            self.retorna_elemento('XPATH', "//option[@label='Excel Spreadsheet (Excel 2007 or later)']").click()

            #colocando o nome do relatório
            self.retorna_elemento('XPATH', '//*[@id="qr-export-modal-custom-filename"]').clear()
            time.sleep(3)
            self.retorna_elemento('XPATH', '//*[@id="qr-export-modal-custom-filename"]').send_keys('relatorio.xlsx')
            time.sleep(3)
            #seleciona "conforme exibido na tabela de dados"
            self.retorna_elemento('XPATH', "//input[@aria-label='Resultados – conforme exibidos na tabela de dados']").click()
            time.sleep(1)

            #seleciona "sem formatação"
            self.retorna_elemento('XPATH', "//input[@aria-label='Valores – não formatados']").click()
            time.sleep(1)

            #clica em baixar csv
            self.retorna_elemento('ID', 'qr-export-modal-download').click()
            time.sleep(3)
            self.aguarda_download()
            caminho_inicio = configActive.DIRETORIO_ARQUIVOS_TEMP + '\\' + 'relatorio.xlsx'
            caminho_fim = configActive.DIRETORIO_ARQUIVOS + '\\' + self.dia_anterior + '\\' + self.dia_anterior + '-' + 'relatorio_Active.xlsx'
            self.renomar_arquivo(caminho_inicio, caminho_fim)
        else:
            print('não há tabela para ser baixada')
            status = {'Status' : ['Nenhuma campnha rodou ontem']}
            df = pd.DataFrame(status)
            df.to_excel('nenhuma_tabela_encontrada.xlsx')
            caminho_inicio = 'nenhuma_tabela_encontrada.xlsx'
            caminho_fim = configActive.DIRETORIO_ARQUIVOS + '\\' +  self.dia_anterior + '\\' + self.dia_anterior + '-' + 'nenhuma_tabela_encontrada.xlsx'
            self.renomar_arquivo(caminho_inicio, caminho_fim)


            
        
    def run(self):
        self.cria_diretorio(configActive.DIRETORIO_ARQUIVOS + '\\' + self.dia_anterior)
        for credencial in configActive.CREDENCIAIS:
            self.login(credencial['usuario'], credencial['senha'])
            self.baixa_relatorio_performance()  
            
        self.driver.close()
        self.driver.quit()
   

if __name__ == '__main__':    
    tentativas = 0
    while (tentativas<3):
        try:
            bot = Bot()
            tentativas = 3
        except Exception as e:
            print(e)
            tentativas += 1
            if (tentativas >=3):
                with open (r'C:\apis\APIActive\log\log.txt', 'w') as arq:
                    arq.write(str(e))
          
        time.sleep(30)