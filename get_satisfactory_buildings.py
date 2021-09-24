import requests
from bs4 import BeautifulSoup
import json

print('Hello world')

page = requests.get('https://satisfactory.fandom.com/wiki/Category:Buildings')
buildings_soup = BeautifulSoup(page.content, "html.parser")

building_pages = buildings_soup.find(id="mw-pages")
building_pages_links = building_pages.find_all('a')
i = 0
buildings = []
for link in building_pages_links:
    i = i + 1
    print(link.get_text() + ' - ' + link.get('href'))
    if i > 10:
        break
    if '/' in link.get_text().lower().replace('/wiki/', ''):
        print('Skippen')
        continue
    page = requests.get('https://satisfactory.fandom.com/' + link.get('href'))
    building_page = BeautifulSoup(page.content, "html.parser")
    infobox = building_page.find("aside", {"class": "portable-infobox"})
    #print(infobox)
    if infobox is None:
        continue
    building = {}
    def has_data_source(tag):
        return tag.has_attr('data-source')
    for item in infobox.find_all(has_data_source):
        if item.get('data-source') is None:
            continue
        if item.find('div') is not None:
            value = item.find('div').get_text()
        else:
            value = item.get_text()
        building[item.get('data-source')] = value
        #print(item.get('data-source') + ': ' + value)
    buildings.append(building)
print(buildings)


with open('buildings.json', 'w') as outfile:
    json.dump(buildings, outfile)