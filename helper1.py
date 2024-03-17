## File for tasks 1-5

import requests
import aiohttp
import asyncio
import re
import json
from datetime import datetime
from functools import wraps
from itertools import chain


class BibEntry:
    """###One single bibliographical entry
    Contains:
    * authors - a string of all author names
    * title - the title of the document
    * source - the publisher of the document
    * physical_desc - the physical description of the document
    * tome - the tome information of the document

    Methods:
    * peek() - quickly print the contents of the entry
    * __str__ - convert the entire bibliographic entry to a string
    """

    def __init__(self, authors: str, title: str, source: str, physical_desc: str, tome: str) -> None:
        self.authors = authors
        self.title = title
        self.source = source
        self.physical_desc = physical_desc
        self.tome = tome

    def peek(self):
        """Print the contents of the entry, testing function"""
        print(f'{self.authors} {self.title} // {self.source} {self.physical_desc} ! Том: {self.tome}')

    def __str__(self):
        """Return the contents of the entry."""
        return f'{self.authors} {self.title} // {self.source} {self.physical_desc} ! Том: {self.tome}'


class Logger:
    """The class for logging informational messages, used for debugging."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def __init__(self, verbosity: bool) -> None:
        self.verbosity = verbosity

    def log(self, text, color=HEADER):
        if self.verbosity:
            print(f'{color} {text} {self.ENDC}')


def handler(func):
    """Decorator function, prints exceptions instead of exiting."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return f'Something went wrong, try again:\nFull exception:\n{e}'
    return wrapper


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
    exists = False
    pob, dob, pod, dod = None, None, None, None
    pobdesc, poddesc = None, None

    # Check if person exists in wiki
    if verbosity:
        print('Checking if a person exists in wiki...')
    R1 = requests.get(url=URL, params=PARAMS1)
    data = R1.json()
    searchinfo = data['query']['searchinfo']
    searchresults = data['query']['search']

    if searchinfo['totalhits'] == 0:
        if verbosity:
            print('Not found, exiting')
        return None

    # if exists, get the page id
    if searchresults[0]['title'].replace(',', '') == person:
        exists = True
        if verbosity:
            print('Found')
        pageid = searchresults[0]['pageid']

    if not exists:
        return None

    # Obtain the wikimedia unique id
    if verbosity:
        print('Obtaining the wikimedia unique id')

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
        print('Error getting wikimedia id, no further information can be accessd.')
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

    if verbosity:
        print('Fetching dates and places.')

    R3 = requests.get(url=URL2, params=PARAMS3)
    try:
        data = R3.json()['entities'][wikibase_id]['claims']
    except KeyError:
        if verbosity:
            print('No claims for wikimedia id found, no further info can be obtained')
        return [None, None, None, None, None, None]

    try:
        dobraw = data['P569'][0]['mainsnak']['datavalue']['value']['time']  # Date of Birth
        pobid = data['P19'][0]['mainsnak']['datavalue']['value']['id']  # Place of Birth id
    except KeyError:
        if verbosity:
            print('Error fetching date of birth or place of birth id')
    try:
        dodraw = data['P570'][0]['mainsnak']['datavalue']['value']['time']  # Date of Death
        podid = data['P20'][0]['mainsnak']['datavalue']['value']['id']  # Place of Death id
    except KeyError:
        if verbosity:
            print('Error fetching date of death or place of death id')

    # Find places of birth from ids
    PARAMS3['props'] = 'labels|descriptions'
    PARAMS3['ids'] = pobid
    R4 = requests.get(url=URL2, params=PARAMS3)
    PARAMS3['ids'] = podid
    R5 = requests.get(url=URL2, params=PARAMS3)

    try:
        pob = R4.json()['entities'][pobid]['labels'][f'{locale}']['value']
    except KeyError:
        if verbosity:
            print('Error fetching place of birth description')
    try:
        pod = R5.json()['entities'][podid]['labels'][f'{locale}']['value']
    except KeyError:
        if verbosity:
            print('Error fetching place of death description')

    # Get descriptions
    try:
        pobdesc = R4.json()['entities'][pobid]['descriptions'][f'{locale}']['value']
    except KeyError:
        if verbosity:
            print('Error fetching place of birth description')

    try:
        poddesc = R5.json()['entities'][podid]['descriptions'][f'{locale}']['value']
    except KeyError:
        if verbosity:
            print('Place of Death Description not found')
    # Convert the datetimes from str to datetime
    dob = datetime.strptime(dobraw, '+%Y-%m-%dT%H:%M:%SZ')
    dod = datetime.strptime(dodraw, '+%Y-%m-%dT%H:%M:%SZ')
    if verbosity:
        print('Done!')
    return [dob, dod, pob, pod, pobdesc, poddesc]


async def rslsearch(person, verbosity=False, parallel=True) -> (None | list[BibEntry]):
    """
    ###Search for a person on the russian state library website.
    ## Args:
        * `person (str)` - name of the person to look up
        * `verbosity (bool, default=False)` - [OPTIONAL] print additional information
        * `parallel (bool, default=True)` - [OPTIONAL] speed up the search by using asynchronous requests
    ## Returns:
        * `None` - this person does not exist in the rsl
        * `list[BibEntry]` - list of bibliographical entries found in the rsl
    """

    async def fetch_pages(session, url, data, num):
        data['SearchFilterForm[page]'] = num + 1
        async with session.get(url, data=data, timeout=10) as response:
            r_l = await response.text()
            return re.findall(PATTERN, json.loads(r_l)['content'])

    async def fetch_entry(session, url):
        URL2 = 'https://search.rsl.ru'
        async with session.get(URL2+url, timeout=10) as response:
            hit = await response.text()
            author = ' '.join(re.findall(r'<td itemprop="author">(.*?)<\/td>', hit))
            title = ' '.join(re.findall(r'<td itemprop="name">(.*?)<\/td>', hit))
            publisher = ' '.join(re.findall(r'<th>Выходные данные<\/th><td>(.*?)<\/td>', hit))
            physical_desc = ' '.join(re.findall(r'<th>Физическое описание<\/th><td>(.*?)<\/td>', hit))
            tome = ' '.join(re.findall(r'<th>Том<\/th><td>(.*?)<\/td>', hit))
            return BibEntry(author, title, publisher, physical_desc, tome)

    def non_parallel_rslsearch(logger, URL, URL2, PATTERN, reqdata):
        logger.log('Non-parallel search specified, starting...')
        entries = []
        r = requests.get(URL, data=reqdata).json()
        maxpage = r['MaxPage']
        totalhits = r['TotalHits']
        logger.log(f'Found, number of pages: {maxpage}, number of hits {totalhits}; Fetching pages')

        hits = re.findall(PATTERN, r['content'])
        for i in range(1, r['MaxPage']):
            reqdata['SearchFilterForm[page]'] = i + 1
            r_l = requests.get(URL, data=reqdata).json()
            hits.extend(re.findall(PATTERN, r_l['content']))

        logger.log('Gathering bibliographical info...')
        for p in hits:
            hit = requests.get(URL2+p).text
            author = ' '.join(re.findall(r'<td itemprop="author">(.*?)<\/td>', hit))
            title = ' '.join(re.findall(r'<td itemprop="name">(.*?)<\/td>', hit))
            publisher = ' '.join(re.findall(r'<th>Выходные данные<\/th><td>(.*?)<\/td>', hit))
            physical_desc = ' '.join(re.findall(r'<th>Физическое описание<\/th><td>(.*?)<\/td>', hit))
            tome = ' '.join(re.findall(r'<th>Том<\/th><td>(.*?)<\/td>', hit))
            entries.append(BibEntry(author, title, publisher, physical_desc, tome))
        logger.log('Done!')
        return entries

    logger = Logger(verbosity=verbosity)
    URL = 'https://search.rsl.ru/site/ajax-search?language=ru'
    URL2 = 'https://search.rsl.ru'
    PATTERN = r'href=\"(\/ru\/record\/\d*?)\"'
    reqdata = {
        "SearchFilterForm[sortby]": "default",
        "SearchFilterForm[page]": "1",
        "SearchFilterForm[search]": f"author:(\"{person.replace(' ', '+')}\")",
        "SearchFilterForm[fulltext]": "0",
        "SearchFilterForm[updatedFields][]": "search"}

    entries = []

    logger.log('Starting the RSL search...')

    if not parallel:
        return non_parallel_rslsearch(logger, URL, URL2, PATTERN, reqdata)

    r = requests.get(URL, data=reqdata).json()
    hits = re.findall(PATTERN, r['content'])
    maxpage = r['MaxPage']
    totalhits = r['TotalHits']

    logger.log(f'Found, number of pages: {maxpage}, number of hits {totalhits}; Fetching pages')

    async with aiohttp.ClientSession() as session1:
        tasks1 = [fetch_pages(session1, URL, reqdata, i) for i in range(1, maxpage)]
        results1 = await asyncio.gather(*tasks1)
        results1 = list(set(chain(*results1)))
        hits.extend(results1)

    logger.log(f'Found {len(hits)} pages')
    if len(hits) > 50:
        logger.log('Sleeping to prevent rate limits')
        await asyncio.sleep(5)
    logger.log('Gathering bibliographical info...')
    async with aiohttp.ClientSession() as session2:
        tasks2 = [fetch_entry(session2, p) for p in hits]
        results2 = await asyncio.gather(*tasks2)

        entries.extend(results2)
    logger.log('Done!')
    return entries


def tester():
    """Temporary testing function."""
    persontest1 = 'Русаков Михаил Петрович'
    # persontest2 = 'Обручев Владимир Афанасьевич'
    # persontest3 = 'Сумгин Михаил Иванович'
    # persontest4 = 'Вознесенский Владимир Александрович'
    res = asyncio.run(rslsearch(persontest1, verbosity=True, parallel=True))
    # print('\n'.join(list(map(str, r  es))))
    print(len(res))


tester()
