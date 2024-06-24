import requests
from helper.handlers import handler
from helper.logger import Logger
from localisation import default


L = default['scrapers']['higeosearch']


@handler
def higeosearch(person, verbosity=False) -> bool:
    """
    ### Find out whether a person exists on higeo.ginras.ru.
    ## Args:
        * `person (str)` - name of the person to look up
        * `verbosity (bool, default=False)` - [OPTIONAL] print additional information
    ## Returns:
        * `bool` - whether the record of the person exists or not
    """
    logger = Logger(verbosity=verbosity)
    logger.log(L['start'])
    r = requests.get(f"http://higeo.ginras.ru/cgi-bin/export.rb?template_name=_default.person&filter=\
                     (COALESCE(person.name, '') = '{person}')&sort=person.author.name").text
    logger.log(L['done'])
    return person in r
