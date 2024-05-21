import requests
import asyncio
import json
import re
from itertools import chain
import aiohttp
from helper.bibentry import BibEntry
from helper.handlers import async_handler
from helper.logger import Logger


@async_handler
async def rslsearch(person, verbosity=False, parallel=True) -> (None | list[BibEntry]):
    """
    ### Search for a person on the russian state library website.
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

    if totalhits > 75:
        logger.log('Too large for parallel search, starting the non-parallel search')
        return non_parallel_rslsearch(logger, URL, URL2, PATTERN, reqdata)

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
