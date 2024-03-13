## File for tasks 1-5

import requests
import json


def wikisearch(person):
    """Search for a person on wikipedia."""
    exists = False
    URL = "https://ru.wikipedia.org/w/api.php"

    # Check if person exists in wiki
    PARAMS1 = {
        "action": "query",
        "format": "json",
        "list": "search",
        "sites": "ruwiki",
        "srsearch": person
    }

    R = requests.get(url=URL, params=PARAMS1)
    data = R.json()
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

    R1 = requests.get(url=URL, params=PARAMS2)
    wikibase_id = R1.json()['query']['pages'][0]['pageprops']['wikibase_item']
    print(wikibase_id)
    return R.json()


persontest = "Русаков Михаил Петрович"
res = wikisearch(persontest)
