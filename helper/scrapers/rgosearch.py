import requests
from bs4 import BeautifulSoup
import asyncio
import aiohttp
from helper.logger import Logger
from helper.handlers import async_handler


@async_handler
async def rgo_check(name, verbosity=True, parallel=True):
    logger = Logger(verbosity=verbosity)
    logger.log('Checking if a person exists in rgo...')
    URL = f"https://elib.rgo.ru/simple-search?location=%2F&query={name}&rpp=10&sort_by=score&order=desc"
    htm = requests.get(URL).text
    if requests.get(URL).status_code != 200:
        return ["Рго не отвечает...", ]

    soup = BeautifulSoup(htm, "html.parser")
    notfoud = soup.find("main", class_="main ml-md-5 mr-md-5 mr-xl-0 ml-xl-0").find("p")
    params = {'query': name,
              'rpp': '10',
              'sort_by': 'score',
              'order': 'desc',
              'etal': '0',
              'start': '0'}

    async def fetch_crds(paramsf, j, session):
        # urlsec = requests.get("https://elib.rgo.ru/simple-search", params=params).text
        paramsf['start'] = str(j)
        async with session.get(URL, params=paramsf, timeout=10) as response:
            resf = []
            hit = await response.text()
            sou = BeautifulSoup(hit, "html.parser")
            textres = sou.find("div", class_="discovery-result-results").find_all("b")
            urlres = sou.find("div", class_="discovery-result-results").find_all(class_="button button-primary mt-2")
            cnt = 0
            for i in textres:
                textres[cnt] = i.string.replace("\n                                ", "")
                urlres[cnt] = f"https://elib.rgo.ru/{str(urlres[cnt])[45:68]}"
                resf.append(textres[cnt])
                resf.append(str(urlres[cnt]))
                cnt += 1
            return resf

    def non_parallel_rgo_check(logger, params, limit):
        res = {}
        logger.log('Obtaining a description from the cards')

        for j in range(0, int(limit), 10):
            params['start'] = str(j)
            urlsec = requests.get("https://elib.rgo.ru/simple-search", params=params).text
            sou = BeautifulSoup(urlsec, "html.parser")
            textres = sou.find("div", class_="discovery-result-results").find_all("b")
            urlres = sou.find("div", class_="discovery-result-results").find_all(class_="button button-primary mt-2")
            cnt = 0
            for i in textres:
                textres[cnt] = i.string.replace("\n                                ", "")
                urlres[cnt] = f"https://elib.rgo.ru/{str(urlres[cnt])[45:68]}"
                res[textres[cnt]] = str(urlres[cnt])
                cnt += 1
        logger.log("Done!")
        return res

    if notfoud is None:
        limit = str(soup.find("div", class_="pagination").find("span", class_="c-mid-blue").string).split(" ")[-1]
        limit = str(soup.find("div", class_="pagination").find("span", class_="c-mid-blue").string).split(" ")[-1]
        if not parallel:
            return non_parallel_rgo_check(logger, params, limit)
        entries = []
        logger.log('Obtaining a description from the cards')
        logger.log("Done!")
        async with aiohttp.ClientSession() as session1:
            task1 = [fetch_crds(params, j, session1) for j in range(0, int(limit) - 1, 10)]
            results1 = await asyncio.gather(*task1)
            entries.extend(results1)
        return entries
    else:
        logger.log("Not found, exiting")
        return [notfoud.string, ]
