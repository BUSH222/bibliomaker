## File for tasks 1-5

import requests
from datetime import datetime


def wikisearch(person, locale='ru'):
    """Search for a person on wikipedia.

    Inputs:
            person (string) - name of the person to look up
            locale (string, default='ru') - [OPTIONAL] wiki language
    Output:
            list or NoneType
            list:
                - Date of Birth (Datetime or NoneType)
                - Date of Death (Datetime or NoneType)
                - Place of Birth (string or NoneType)
                - Place of Death (string or NoneType)
    """

    # Constants
    URL = f"https://{locale}.wikipedia.org/w/api.php"
    URL2 = "https://www.wikidata.org/w/api.php"
    PARAMS1 = {
        "action": "query",
        "format": "json",
        "list": "search",
        "sites": f"{locale}wiki",
        "srsearch": person
    }
    # Initialising Variables
    exists = False
    pob, dob, pod, dod = None, None, None, None

    # Check if person exists in wiki
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
        "sites": f"{locale}wiki",
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
               "sites": f"{locale}wiki",
               "props": "claims",
               "formatversion": "2"}
    R3 = requests.get(url=URL2, params=PARAMS3)
    data = R3.json()['entities'][wikibase_id]['claims']
    dobraw = data["P569"][0]['mainsnak']['datavalue']['value']['time']  # Date of Birth
    dodraw = data["P570"][0]['mainsnak']['datavalue']['value']['time']  # Date of Death
    pobid = data["P19"][0]['mainsnak']['datavalue']['value']['id']  # Place of Birth id
    podid = data["P20"][0]['mainsnak']['datavalue']['value']['id']  # Place of Death id

    # Find places of birth from ids
    PARAMS3['props'] = 'labels'
    PARAMS3['ids'] = pobid
    R4 = requests.get(url=URL2, params=PARAMS3)
    PARAMS3['ids'] = podid
    R5 = requests.get(url=URL2, params=PARAMS3)

    pob = R4.json()['entities'][pobid]['labels'][f'{locale}']['value']
    pod = R5.json()['entities'][podid]['labels'][f'{locale}']['value']
    # Convert the datetimes from str to datetime
    dob = datetime.strptime(dobraw, '+%Y-%m-%dT%H:%M:%SZ')
    dod = datetime.strptime(dodraw, '+%Y-%m-%dT%H:%M:%SZ')
    return [dob, dod, pob, pod]


def tester():
    """Temporary testing function"""
    persontest1 = "Русаков Михаил Петрович"
    # persontest2 = "Обручев Владимир Афанасьевич"
    # persontest3 = "Сумгин Михаил Иванович"
    # persontest4 = "Вознесенский Владимир Александрович"
    res = wikisearch(persontest1)
    print(res)


tester()
