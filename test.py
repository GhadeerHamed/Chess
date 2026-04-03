import requests
from bs4 import BeautifulSoup
import json

response = requests.get('https://en.wikipedia.org/wiki/List_of_country_calling_codes')

soup = BeautifulSoup(response.content, 'html.parser')

table = soup.find('table', {'class': 'wikitable sortable sticky-header-multi'})

allrows = table.findAll('tr')

myList = []

for each in allrows:
  allData = each.findAll('td')
  if(len(allData)>1):
    myList.append([allData[0].text.strip(), allData[1].text.strip()])

print("====> ", myList)
print(len(myList))
