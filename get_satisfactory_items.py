import requests
from bs4 import BeautifulSoup
import json
from modules.beautiful_soup_helpers import table_to_2d
import re

print('Hello world')

page = requests.get('https://satisfactory.fandom.com/wiki/Category:Items')
pagesoup = BeautifulSoup(page.content, "html.parser")

pagediv = pagesoup.find(id="mw-pages")
links = pagediv.find_all('a')
i = 0
item_list = []
recipe_list = []
for link in links:
    i = i + 1
    print(link.get_text() + ' - ' + link.get('href'))
    if i > 9:
         break
    if '/' in link.get_text().lower().replace('/wiki/', '') or '\%EC\%B' in link.get_text().lower():
        print('Skippen')
        continue
    page = requests.get('https://satisfactory.fandom.com/' + link.get('href'))
    soup_page = BeautifulSoup(page.content, "html.parser")
    infobox = soup_page.find("aside", {"class": "portable-infobox"})
    if infobox is None:
        continue
    single_item = {}

    def has_data_source(tag):
        return tag.has_attr('data-source')
    for item in infobox.find_all(has_data_source):
        print(999, item.get('data-source'), item.get_text())
        if item.get('data-source') is None:
            continue
        if item.find('div') is not None:
            value = item.find('div').get_text()
        else:
            value = item.get_text()
        single_item[item.get('data-source')] = value
        #print(item.get('data-source') + ': ' + value)
    sink_value = infobox.find('a', {"href": "/wiki/AWESOME_Sink"})
    if sink_value is not None:
        single_item['sink_value'] = sink_value.parent.find_next('div').get_text()
    item_list.append(single_item)


    # Get recipes
    obtaining = soup_page.find(id="Obtaining")
    crafting = obtaining.find_next(id="Crafting")
    if crafting is None:
        continue
    craftingtable = crafting.find_next("table")
    recipes = table_to_2d(craftingtable)
    columns = len(recipes[0])
    
    for recipe in recipes[1:]:
        #print(recipe)
        current_column = 1
        inputs = []
        outputs = []
        recipe_object = {}
        recipe_object['recipename'] = recipe[0].replace('Alternate', '')
        recipe_object['alternate'] = True if recipe[0].endswith('Alternate') else False
        previous_column = ''
        for recipecolumn in recipe[1:]:
            column_name = recipes[0][current_column]
            current_column = current_column + 1
            if recipecolumn == previous_column:
                continue
            elif column_name == "Building":
                recipemachine = recipecolumn
                first_digit = re.search(r"\d", recipecolumn).start()
                recipemachine = recipecolumn[0:first_digit]
                recipe_sec = int(recipecolumn[first_digit:].replace(' sec', '').replace(' × ', ''))
            elif column_name == 'Prerequisites':
                recipe_object['prerequisites'] = recipecolumn
            elif recipecolumn == '\xa0':
                pass
            elif column_name == "Ingredients":
                recipeinput = recipecolumn.split(' × ')
                first_digit = re.search(r"\d", recipeinput[1]).start()
                recipe_min = float(recipeinput[1][first_digit:].split(' / min')[0])
                productname = recipeinput[1].replace(f"{str(recipe_min).replace('.0', '')} / min", '')
                inputs.append({"product": productname, "amount": int(recipeinput[0]), "recipe_min": recipe_min})
            elif column_name == "Products":
                recipeinput = recipecolumn.split(' × ')
                recipe_mj = float(re.search(r'/ min(.*) MJ', recipeinput[1]).group(1))
                first_digit = re.search(r"\d", recipeinput[1]).start()
                recipe_min = float(recipeinput[1][first_digit:].split(' / min')[0])
                print(999, recipeinput[1], f"{recipe_min} / min{recipe_mj} MJ/item")
                productname = recipeinput[1].replace(f"{str(recipe_min).replace('.0', '')} / min{str(recipe_mj).replace('.0', '')} MJ/item", '')
                outputs.append({"product": productname, "amount": int(recipeinput[0]), "recipe_min": recipe_min, "mj": recipe_mj})
            previous_column = recipecolumn
        recipe_object['inputs'] = inputs
        recipe_object['outputs'] = outputs
        recipe_object['machine'] = recipemachine
        recipe_object['machine_seconds'] = recipe_sec
        recipe_list.append(recipe_object)



print(item_list, recipe_list)


with open('items.json', 'w') as outfile:
    json.dump(item_list, outfile)
with open('recipes.json', 'w') as outfile:
    json.dump(recipe_list, outfile)