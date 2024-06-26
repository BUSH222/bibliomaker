import requests
from bs4 import BeautifulSoup
import asyncio
import aiohttp
from helper.handlers import async_handler
from helper.logger import Logger
from localisation import default


L = default['scrapers']['rnbsearch']


@async_handler
async def rnb_check(name, verbosity=True, parallel=True):
    logger = Logger(verbosity=verbosity)
    logger.log(L['start'])
    URL = f"https://nlr.ru/e-case3/sc2.php/web_gak/ss?text={name}&x=15&y=17"
    htm = requests.get(URL).text
    soup = BeautifulSoup(htm, "html.parser")
    allcards = soup.find("div", id="row1textmain").find("div", class_="text").find_all("a", href_="")
    logger.log(L['description'])

    async def fetch_pict(j, session, URLCRDS):
        URLCRD = URLCRDS[:-1] + str(j)
        async with session.get(URLCRD) as respcrd:
            resf = []
            hitcrd = await respcrd.text()
            soupcrd = BeautifulSoup(hitcrd, "html.parser")
            heading = soupcrd.find("div", class_="center").find("b").string
            pict = soupcrd.find("img", class_="card")["src"]
            stroka = f"https://nlr.ru{pict}"
            resf.append(heading[:-1])
            resf.append(stroka)
        return resf

    async def fetch_info(i1, session):
        if name in str(i1.string):
            URLCRDS = "https://nlr.ru/e-case3/sc2.php/web_gak{}".format(str(i1["href"])[2:])
            async with session.get(URLCRDS) as response:
                hit = await response.text()
                soupcrds = BeautifulSoup(hit, "html.parser")
                resf = []
                heading = soupcrds.find("div", class_="center").find("b").string
                limit = int(heading.split(" ")[-1][:-1])
                taskf = [fetch_pict(j, session, URLCRDS) for j in range(1, limit + 1)]
                resf = await asyncio.gather(*taskf)
                return resf

    def non_parallel_rnb_check():
        out = {}
        for i in allcards:
            if name in str(i.string):
                # res[i.string] = "https//nlr.ru/e-case3/sc2.php/web_gak{}".format(str(i["href"])[2:])
                URLCRDS = "https://nlr.ru/e-case3/sc2.php/web_gak{}".format(str(i["href"])[2:])
                htmcrds = requests.get(URLCRDS).text
                soupcrds = BeautifulSoup(htmcrds, "html.parser")
                heading = soupcrds.find("div", class_="center").find("b").string
                limit = int(heading.split(" ")[-1][:-1])

                for j in range(1, limit + 1):
                    URLCRD = URLCRDS[:-1] + str(j)
                    htmcrd = requests.get(URLCRD).text
                    soupcrd = BeautifulSoup(htmcrd, "html.parser")
                    heading = soupcrd.find("div", class_="center").find("b").string
                    pict = soupcrd.find("img", class_="card")["src"]
                    out[heading[:-1]] = f"https://nlr.ru{pict}"
    if not parallel:
        return non_parallel_rnb_check()
    else:
        dictres = {}
        async with aiohttp.ClientSession() as session1:
            task1 = [fetch_info(i, session1) for i in allcards]
            results1 = await asyncio.gather(*task1)
            results1 = results1[1]
        logger.log(L['done'])
        if results1 is None:
            dictres[""] = L['not_found']
            return dictres
        for k in results1:
            dictres[k[0]] = k[1]
        return dictres
