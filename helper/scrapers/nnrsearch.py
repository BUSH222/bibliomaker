import requests
from bs4 import BeautifulSoup
import re
from helper.handlers import async_handler
from helper.logger import Logger


@async_handler
async def nnr_check(name, verbosity=True):
    logger = Logger(verbosity=verbosity)
    logger.log('Checking if a person exists in nnr. ..')
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
