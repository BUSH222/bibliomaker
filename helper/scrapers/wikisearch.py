import requests
from helper.handlers import handler
from helper.logger import Logger
from localisation import default


L = default['scrapers']['wikisearch']


@handler
def wikisearch(person, locale='ru', verbosity=False) -> (list[None] | list | None):
    """
    ### Search for a person on wikipedia.
    ## Args:
        * `person (str)` - name of the person to look up
        * `locale (str, default='ru')` - [OPTIONAL] wiki language
        * `verbosity (bool, default=False)` - [OPTIONAL] print additional information
    ## Returns:
        * `list`:
            - Date of birth (Datetime or None)
            - Date of death (Datetime or None)
            - Place of birth (str or None)
            - Place of death (str or None)
            - Description of place of birth (str or None)
            - Descriptions of place of death (str or None)
        * `None` - the person does not exist in wikipedia.
        * `list[None]` - the person exists in wikipedia but no information can be obtained.
    """

    # Constants
    URL = f'https://{locale}.wikipedia.org/w/api.php'
    URL2 = 'https://www.wikidata.org/w/api.php'
    PARAMS1 = {
        'action': 'query',
        'format': 'json',
        'list': 'search',
        'sites': f'{locale}wiki',
        'srsearch': person
    }
    # Initialising Variables
    logger = Logger(verbosity=verbosity)
    exists = False
    pob, pod = None, None
    pobdesc, poddesc = None, None

    # Check if person exists in wiki
    logger.log(L['start'])
    R1 = requests.get(url=URL, params=PARAMS1)
    data = R1.json()
    searchinfo = data['query']['searchinfo']
    searchresults = data['query']['search']

    if searchinfo['totalhits'] == 0:
        if verbosity:
            logger.log(L['not_found'], color=Logger.FAIL)
        return None

    # if exists, get the page id
    if searchresults[0]['title'].replace(',', '') == person:
        exists = True
        logger.log(L['found'])
        pageid = searchresults[0]['pageid']

    if not exists:
        return None

    # Obtain the wikimedia unique id
    logger.log(L['wikimedia_id_start'])

    PARAMS2 = {
        'action': 'query',
        'format': 'json',
        'prop': 'pageprops',
        'pageids': pageid,
        'formatversion': '2',
        'sites': f'{locale}wiki',
    }

    R2 = requests.get(url=URL, params=PARAMS2)
    try:
        wikibase_id = R2.json()['query']['pages'][0]['pageprops']['wikibase_item']
    except KeyError:
        logger.fail(L['error_wikimedia'])
        return [None, None, None, None, None, None]

    # Obtain the necessary information from wikibase
    # P numbers:
    # Date of Birth: P569
    # Date of Death: P570
    # Place of Birth: P19
    # Place of Death: P20

    PARAMS3 = {'action': 'wbgetentities',
               'format': 'json',
               'ids': wikibase_id,
               'sites': f'{locale}wiki',
               'props': 'claims',
               'formatversion': '2'}

    logger.log(L['dates_start'])

    R3 = requests.get(url=URL2, params=PARAMS3)
    try:
        data = R3.json()['entities'][wikibase_id]['claims']
    except KeyError:
        if verbosity:
            logger.fail(L['error_no_claims'])
        return [None, None, None, None, None, None]

    try:
        dobraw = data['P569'][0]['mainsnak']['datavalue']['value']['time']  # Date of Birth
        pobid = data['P19'][0]['mainsnak']['datavalue']['value']['id']  # Place of Birth id
    except KeyError:
        logger.fail(L['error_dob_pob'])
    try:
        dodraw = data['P570'][0]['mainsnak']['datavalue']['value']['time']  # Date of Death
        podid = data['P20'][0]['mainsnak']['datavalue']['value']['id']  # Place of Death id
    except KeyError:
        logger.fail(L['error_dod_pod'])

    # Find places of birth from ids
    PARAMS3['props'] = 'labels|descriptions'
    PARAMS3['ids'] = pobid
    R4 = requests.get(url=URL2, params=PARAMS3)
    PARAMS3['ids'] = podid
    R5 = requests.get(url=URL2, params=PARAMS3)

    try:
        pob = R4.json()['entities'][pobid]['labels'][f'{locale}']['value']
    except KeyError:
        logger.fail(L['error_pob'])
    try:
        pod = R5.json()['entities'][podid]['labels'][f'{locale}']['value']
    except KeyError:
        logger.fail(L['error_pod'])

    # Get descriptions
    try:
        pobdesc = R4.json()['entities'][pobid]['descriptions'][f'{locale}']['value']
    except KeyError:
        logger.fail(L['error_pob'])

    try:
        poddesc = R5.json()['entities'][podid]['descriptions'][f'{locale}']['value']
    except KeyError:
        logger.fail(L['error_pod'])
    if verbosity:
        logger.log(L['done'])
    return [dobraw, dodraw, pob, pod, pobdesc, poddesc]
