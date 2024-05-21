import requests
from bs4 import BeautifulSoup
import asyncio
import aiohttp
from helper.handlers import async_handler
from helper.logger import Logger


@async_handler
async def spb_check(name, verbosity=True, parallel=True):
    logger = Logger(verbosity=verbosity)
    logger.log('Checking if a person exists in spb...')
    URL = 'https://primo.nlr.ru/primo_library/libweb/action/search.do'
    params = {
        'fn': 'search',
        'vl(freeText0)': name
    }
    hitfirst = requests.get(URL, params=params).text
    soup = BeautifulSoup(hitfirst, "html.parser")

    limit = int(soup.find("div", id="resultsNumbersTile").find("em").string)
    pagcnt = ((limit + 19) // 20)
    bodyres = []
    logger.log('Obtaining a description from the cards')

    def non_parallel_spb_check(logger):
        for page in range(1, pagcnt + 1):
            if page == 1:
                hit = requests.get(URL, params=params).text
            else:
                pageind = 1 + (page - 2) * 20  # формула успеха
                pageparams = {'pag': 'nxt',
                              'indx': pageind,
                              'pageNumberComingFrom': '1',
                              'indx': pageind,
                              'fn': 'search',
                              'dscnt': '0',
                              'scp.scps': 'scope:(MAIN_07NLR)',
                              'vid': '07NLR_VU1',
                              'mode': 'Basic',
                              'ct': 'search',
                              'srt': 'rank',
                              'tab': 'default_tab',
                              'dum': 'true',
                              'vl(freeText0)': name}
                hit = requests.get(URL, params=pageparams).text
            souppage = BeautifulSoup(hit, "html.parser")
            crd = souppage.find_all("h2", class_="EXLResultTitle")
            for i in crd:
                URL2 = i.find("a")["href"]
                surl = requests.get("https://primo.nlr.ru/primo_library/libweb/action/{}".format(URL2))
                sou = BeautifulSoup(surl.text, "html.parser")
                descrip = sou.find("div", class_="EXLDetailsContent").find("li", id="Описание-1").\
                    find("span", class_="EXLDetailsDisplayVal")
                while descrip.string is None:
                    surl = requests.get("https://primo.nlr.ru/primo_library/libweb/action/{}".format(URL2))
                    sou = BeautifulSoup(surl.text, "html.parser")
                    descrip = sou.find("div", class_="EXLDetailsContent").find("li", id="Описание-1").\
                        find("span", class_="EXLDetailsDisplayVal")
                bodyres.append(descrip.string)
        return bodyres

    async def fetch_page(page, session):
        if page == 1:
            pageparams = params
        else:
            pageind = 1 + (page - 2) * 20  # формула успеха
            pageparams = {
                'pag': 'nxt',
                'indx': pageind,
                'pageNumberComingFrom': '1',
                'indx': pageind,
                'fn': 'search',
                'dscnt': '0',
                'scp.scps': 'scope:(MAIN_07NLR)',
                'vid': '07NLR_VU1',
                'mode': 'Basic',
                'ct': 'search',
                'srt': 'rank',
                'tab': 'default_tab',
                'dum': 'true',
                'vl(freeText0)': name}
        async with session.get(URL, params=pageparams) as respage:
            hitpage = await respage.text()
            souppage = BeautifulSoup(hitpage, "html.parser")
            crd = souppage.find_all("h2", class_="EXLResultTitle")
            taskf = [fetch_crd(i.find("a")["href"], session) for i in crd]
            resultf = await asyncio.gather(*taskf)
            return resultf

    async def fetch_crd(URL3, session):
        async with session.get("https://primo.nlr.ru/primo_library/libweb/action/{}".format(URL3)) as respcrd:
            hitcrd = await respcrd.text()
            soucrd = BeautifulSoup(hitcrd, "html.parser")
            des = soucrd.find("div", class_="EXLDetailsContent")
            if des is None:
                des = await fetch_crd(URL3, session)
                return des
            else:
                return des.find("li", id="Описание-1").find("span", class_="EXLDetailsDisplayVal").text.strip()

    if not parallel:
        return non_parallel_spb_check(logger)
    async with aiohttp.ClientSession() as session1:
        task1 = [fetch_page(page, session1) for page in range(1, pagcnt + 1)]
        results1 = await asyncio.gather(*task1)
        logger.log('Done!')
        if results1 == []:
            return [["Нет информации на сайте СПБ"], ]
        return results1
