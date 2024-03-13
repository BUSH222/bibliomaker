## File for tasks 1-5

import requests
from datetime import datetime


def wikisearch(person):
    """Search for a person on wikipedia."""
    exists = False
    URL = "https://ru.wikipedia.org/w/api.php"
    URL2 = "https://www.wikidata.org/w/api.php"
    pob, dob, pod, dod = None, None, None, None

    # Check if person exists in wiki
    PARAMS1 = {
        "action": "query",
        "format": "json",
        "list": "search",
        "sites": "ruwiki",
        "srsearch": person
    }

    R1 = requests.get(url=URL, params=PARAMS1)
    data = R1.json()
    searchinfo = data['query']['searchinfo']
    searchresults = data['query']['search']

    if searchinfo['totalhits'] == 0:
        return None

    # if exists, get the page id
    if searchresults[0]['title'].replace(',', '') == person:
        exists = True
        pageid = searchresults[0]['pageid']

    if not exists:
        return None

    # Obtain the wikimedia unique id

    PARAMS2 = {
        "action": "query",
        "format": "json",
        "prop": "pageprops",
        "pageids": pageid,
        "formatversion": "2",
        "sites": "ruwiki",
    }

    R2 = requests.get(url=URL, params=PARAMS2)
    wikibase_id = R2.json()['query']['pages'][0]['pageprops']['wikibase_item']

    # Obtain the necessary information from wikibase
    # P numbers:
    # Date of Birth: P569
    # Date of Death: P570
    # Place of Birth: P19
    # Place of Death: P20

    PARAMS3 = {"action": "wbgetentities",
               "format": "json",
               "ids": wikibase_id,
               "sites": "ruwiki",
               "props": "claims",
               "formatversion": "2"}
    R3 = requests.get(url=URL2, params=PARAMS3)
    data = R3.json()['entities'][wikibase_id]['claims']
    dobraw = data["P569"][0]['mainsnak']['datavalue']['value']['time']  # Date of Birth
    dodraw = data["P570"][0]['mainsnak']['datavalue']['value']['time']  # Date of Death
    pobid = data["P19"][0]['mainsnak']['datavalue']['value']['id']  # Place of Birth id
    podid = data["P20"][0]['mainsnak']['datavalue']['value']['id']  # Place of Death id

    PARAMS3['props'] = 'labels'
    PARAMS3['ids'] = pobid
    R4 = requests.get(url=URL2, params=PARAMS3)
    PARAMS3['ids'] = podid
    R5 = requests.get(url=URL2, params=PARAMS3)

    pob = R4.json()['entities'][pobid]['labels']['ru']['value']
    pod = R5.json()['entities'][podid]['labels']['ru']['value']

    dob = datetime.strptime(dobraw, '+%Y-%m-%dT%H:%M:%SZ')
    dod = datetime.strptime(dodraw, '+%Y-%m-%dT%H:%M:%SZ')
    return [dob, dod, pob, pod]


persontest1 = "Русаков Михаил Петрович"
persontest2 = "Обручев Владимир Афанасьевич"
persontest3 = "Сумгин Михаил Иванович"
persontest4 = "Вознесенский Владимир Александрович"
res = wikisearch(persontest3)
print(res)
