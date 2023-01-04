import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

class ScrapeSciello:
    show = 100
    URL_scielo = f"https://search.scielo.org/?count={show}&"
 
    def research(self, search: str, limit_page=10):
        # Faça a requisição à página e obtenha o conteúdo HTML
        search = '&q=' + search.replace(' ', '+')
        page = requests.get(self.URL_scielo + search)
        soup = BeautifulSoup(page.content, "html.parser")        

        result = pd.DataFrame()

        n_found = int(soup.find(id="TotalHits").text.replace(' ',''))
        n_pages = int(n_found/self.show)+1

        print(n_found,' resultados em ', self.URL_scielo + search, end='\r')

        pids = []
        titulos = []
        autoria = []
        resumos = []
        urls=[]
        downloads=[]
        citacoes=[]
        publicacoes=[]
        pub_MM=[]
        pub_AA=[]
        volumes=[]
        numeros=[]
        paginas=[]

        if n_pages > limit_page: n_pages = limit_page
        for page in range(n_pages):
            if (page != 0):
                print(self.URL_scielo + '&from='+str(page*self.show+1) + '&page='+str(page+1) + search, end='\r')
                page = requests.get(self.URL_scielo + '&from='+str(page*self.show+1) + '&page='+str(page+1) + search)
                soup = BeautifulSoup(page.content, "html.parser")            
            
            itens = soup.find_all(class_='item')
            for item in itens:
                titulo = item.find(class_='title')
                titulo = re.search(' id="title-(.*?)">(.*?)<',str(titulo))
                pid = titulo.group(1)   #paper id
                pids.append(pid)
                titulos.append(titulo.group(2)) #paper title
                #paper abstract
                try:
                    resumos.append(item.find(class_="abstract", id=re.compile(pid+"-\w*_pt")).text.strip())
                except AttributeError:
                    try:
                        resumos.append(item.find(class_="abstract", id=re.compile(pid+"-\w*_en")).text.strip())
                    except:
                        resumos.append("-")
                #authors
                autores = item.find(class_='line authors')
                if autores is None:
                    autores = '-'
                else:
                    autores = autores.text.replace('\n', '').replace('                                            ',' ')
                autoria.append(autores)
                #metadata
                metadados = item.find(class_='line metadata')                
                url = down = cit = '' 
                dados = metadados.text.strip().split('\n\n') 
                for dd in dados:
                    if ('http' in dd): #https://doi.org/10.1590/S1517-86922009000300010
                        url = dd.strip()
                    elif ('downloads' in dd): #3219 downloads
                        down = dd.split(' ')[0]
                    else:                   #Citado 2 vezes em SciELO
                        cit = dd.strip()
                urls.append(url)
                downloads.append(down)
                citacoes.append(cit)
                #source
                fonte = item.find(class_='line source')
                info = [x for x in fonte.text.replace('\n','  ').split('  ') if x != '']
                publicacoes.append(info[0])
            

        result = result.assign(pid=pids, 
                            titulo=titulos,
                            autoria=autoria,
                            resumo=resumos,
                            url=urls,
                            baixado=downloads,
                            citado=citacoes,
                            fonte=publicacoes,)

        print(end='\r') 
        return result

#ss = ScrapeSciello()
#print(ss.research('sport'))