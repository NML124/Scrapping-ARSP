import requests
from bs4 import BeautifulSoup


url='https://arsp.cd/registre-des-entreprises-enregistrees/'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
links=[]
data=[]
response = requests.get(url,headers=headers)
numberOfSiteDone=0
if response.ok :
    soup=BeautifulSoup(response.text,"html.parser")
    tds= soup.find('tbody')

    #Prendre tous les liens de chaque entreprise
    for td in tds:
        a=td.find('a')
        if str(a)!="-1" and a!=None:
            link=a['onclick']
            link=link[22:110]
            links.append("https://arsp.cd/"+link)

    #Recuperer les informations des entreprise
    for link in links:
        res = requests.get(link,headers=headers)
        if res.ok :
            
            entreprise_info=[]
            soup=BeautifulSoup(res.text,"html.parser")
            table= soup.find('table')
            informations = table.findAll('td')
            for info in informations:
                info_=str(info.text).strip()
                entreprise_info.append(info_)
            data.append(entreprise_info)
            numberOfSiteDone+=1
            print(numberOfSiteDone)
    
    #Ecrire les donnees dans un fichier csv
    with open ('entreprise2.csv','w',encoding="utf-8") as file :
        for enterprise in data:
            for i in range(9):
                file.write(enterprise[i]+"\\")
            file.write("\n")
   


