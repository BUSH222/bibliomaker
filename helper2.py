import requests
from bs4 import BeautifulSoup
import re
from helper1 import Logger, handler
import asyncio



async def rgo_check(name, verbosity=True, parallel=True):
    logger = Logger(verbosity=verbosity)
    logger.log('Checking if a person exists in rgo...')
    URL = f"https://elib.rgo.ru/simple-search?location=%2F&query={name}&rpp=10&sort_by=score&order=desc"
    htm = requests.get(URL).text
    soup = BeautifulSoup(htm, "html.parser")
    notfoud = soup.find("main", class_="main ml-md-5 mr-md-5 mr-xl-0 ml-xl-0").find("p")
    params = {
            'query': name,
            'rpp': '10',
            'sort_by': 'score',
            'order': 'desc',
            'etal': '0',
            'start': '0'
        }
    limit = str(soup.find("div", class_="pagination").find("span", class_="c-mid-blue").string).split(" ")[-1]

    async def fetch_crds(params, j, res):
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
        return res

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
        if not parallel:
            return non_parallel_rgo_check(logger, params)
        
        res = {}
        logger.log('Obtaining a description from the cards')

        task1 = [fetch_crds(params, j, res) for j in range(0, int(limit), 10)]
        await asyncio.gather(*task1)
        logger.log("Done!")
        return res
    else:
        logger.log("Not found, exiting")
        return notfoud.string
    

@handler
def rnb_check(name, verbosity=True):
    logger = Logger(verbosity=verbosity)
    logger.log('Checking if a person exists in rnb...')
    URL = f"https://nlr.ru/e-case3/sc2.php/web_gak/ss?text={name}&x=15&y=17"
    htm = requests.get(URL).text
    soup = BeautifulSoup(htm, "html.parser")
    allcards = soup.find("div", id="row1textmain").find("div", class_="text").find_all("a", href_="")
    out = {}
    logger.log('Obtaining a description from the cards')
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
                out[heading[:-1]] = f'https://nlr.ru{pict}'
    logger.log('Done!')
    return out

@handler
def nnr_check(name, verbosity=True):
    logger = Logger(verbosity=verbosity)
    logger.log('Checking if a person exists in nnr...')
    URL = "http://e-heritage.ru/Catalog/FindPerson"
    data = {
        'maxRow': '1',
        'lang': 'ru',
        'ssf0': '1',
        'opt0': '2',
        'val0': name.split()[0],
        'cov1': '1',
        'ssf1': '2',
        'opt1': '2',
        'val1': name.split()[1],
        'nuDocsOnPage': '10',
        'sortOrder': '---'}
    res = {}
    crdres = {}
    htm = requests.post(URL, data=data).text
    soup = BeautifulSoup(htm, "html.parser")
    urlres = soup.find_all("a")
    logger.log('Obtaining a description from the cards')
    for j in urlres:
        suburl = str(j["href"])
        suburl = requests.get(f"http://e-heritage.ru{suburl}").text
        sou = BeautifulSoup(suburl, "html.parser")
        biores1 = sou.find_all("div", class_="col-4 element_label")
        biores2 = sou.find_all("div", class_="col-6 element_value")
        crdhead = sou.find_all("div", class_="card-header")
        crdbody = sou.find_all("div", class_=re.compile("card-body*"))

        for cnt in range(0, len(biores1)-1):
            res[biores1[cnt].string.replace("\r\n                ", "").replace("    ", "")]\
                = biores2[cnt].string.replace("\r\n                ", "").replace("    ", "")
        for crd in range(0, len(crdhead)):
            divchek = " ".join(list(map(lambda x: x.string, crdbody[crd].find_all("div"))))
            lichek = list(map(lambda x: [x.find("a").string.replace("\r\n                ", ""), x.find("a")["href"]]
                              if x.find("a")["href"][:3] == "htt" else
                              [x.find("a").string.replace("\r\n                ", ""),
                               "http://e-heritage.ru" + x.find("a")["href"]],
                              crdbody[crd].find_all("li")))
            if divchek is None or divchek == "":
                crdres[re.search(r"[а-яА-Я\s]{3,}+", str(crdhead[crd])).group()] = lichek
            else:
                crdres[re.search(r"[а-яА-Я\s]{3,}+", str(crdhead[crd])).group()] = divchek

        res[biores1[-1].string.replace("\r\n                ", "").replace("    ", "")] = \
            [i.string for i in biores2[-1].find_all("li")]
        logger.log('Done!')
        return res, crdres

@handler
def spb_check(name, verbosity=True):
    logger = Logger(verbosity=verbosity)
    logger.log('Checking if a person exists in spb...')
    URL = 'https://primo.nlr.ru/primo_library/libweb/action/search.do'
    params = {
        'fn': 'search',
        'vl(freeText0)': name
    }
    htm = requests.get(URL, params=params).text
    soup = BeautifulSoup(htm, "html.parser")
    crd = soup.find_all("h2", class_="EXLResultTitle")
    headres = []
    bodyres = []
    logger.log('Obtaining a description from the cards')
    for i in crd:
        surl = requests.get("https://primo.nlr.ru/primo_library/libweb/action/{}".format(i.find("a")["href"])).text
        sou = BeautifulSoup(surl, "html.parser")
        descrip = sou.find("div", class_="EXLDetailsContent").find("li", id="Описание-1").\
            find("span", class_="EXLDetailsDisplayVal")
        while descrip.string is None:
            surl = requests.get("https://primo.nlr.ru/primo_library/libweb/action/{}".format(i.find("a")["href"])).text
            sou = BeautifulSoup(surl, "html.parser")
            descrip = sou.find("div", class_="EXLDetailsContent").find("li", id="Описание-1").\
                find("span", class_="EXLDetailsDisplayVal")
        headres.append(sou.find("h1", class_="EXLResultTitle").string)
        bodyres.append(descrip.string)
    logger.log('Done!')
    return headres, bodyres


if __name__ == "__main__":
    # print('\n'.join([f'{key}:   {value}' for key, value in rnb_check('Обручев Владимир Афанасьевич').items()]))
    print(rgo_check("Обручев", parallel=False))