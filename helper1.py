## File for tasks 1-5

import re
import requests


def wikisearch(person):
    """Search for a person on wikipedia."""
    URL = "https://en.wikipedia.org/w/api.php"

    PARAMS = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": person
    }

    R = requests.get(url=URL, params=PARAMS)
    print(R.json())


wikisearch("Nelson Mandela")
