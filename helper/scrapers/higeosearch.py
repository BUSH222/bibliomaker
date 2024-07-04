import requests
from helper.handlers import handler
from helper.logger import Logger
from localisation import default
from bs4 import BeautifulSoup


L = default['scrapers']['higeosearch']


@handler
def higeosearch(person, verbosity=False) -> bool:
    """
    ### Find out whether a person exists on higeo.ginras.ru; search for publications there
    ## Args:
        * `person (str)` - name of the person to look up
        * `verbosity (bool, default=False)` - [OPTIONAL] print additional information
    ## Returns:
        * `bool` - whether the record of the person exists or not
    """
    logger = Logger(verbosity=verbosity)
    logger.log(L['start'])
    res = []
    r = requests.get(f"http://higeo.ginras.ru/cgi-bin/export.rb?template_name=_default.person&filter=\
                     (COALESCE(person.name, '') = '{person}')&sort=person.author.name").text

    if person in r:
        res.append(L['exists'])
    r2name = f'{person.split()[0]} {person.split()[1][0].upper()}.{person.split()[2][0].upper()}'
    r2 = requests.get(f"http://higeo.ginras.ru/cgi-bin/export.rb?template_name=_default.person&filter=\
                      (COALESCE(person.bib, '') LIKE '%{r2name}%')&sort=person.author.name").text
    soup = BeautifulSoup(r2, "html.parser")
    links = []
    for item in soup.find_all('a', href=True):
        if person not in str(item):
            links.append(item['href'])
    
    for link in links:
        e = requests.get('http://higeo.ginras.ru' + link).text
    logger.log(L['done'])
