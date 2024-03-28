import requests
from bs4 import BeautifulSoup
import re


def rgo_check(name):
    URL = f"https://elib.rgo.ru/simple-search?location=%2F&query={name}&rpp=10&sort_by=score&order=desc"
    htm = requests.get(URL).text
    soup = BeautifulSoup(htm, "lxml")
    try:
        page_p = soup.find("main", class_="main ml-md-5 mr-md-5 mr-xl-0 ml-xl-0").find("p").string
        return page_p
    except:
        res = {}
        limit = str(soup.find("div", class_="pagination").find("span", class_="c-mid-blue").string).split(" ")[-1]

        for j in range(0, int(limit), 10):
            urlsec = requests.get(f"https://elib.rgo.ru/simple-search?query=Обручев&sort_by=score&order=desc&rpp=10&etal=0&start={j}").text
            sou = BeautifulSoup(urlsec, "lxml")
            textres = sou.find("div", class_="discovery-result-results").find_all("b")
            urlres = sou.find("div", class_="discovery-result-results").find_all(class_="button button-primary mt-2")
            cnt = 0
        
            for i in textres:
                textres[cnt] = i.string.replace("\n                                ", "")
                urlres[cnt] = f"https://elib.rgo.ru/{str(urlres[cnt])[45:68]}"
                res[textres[cnt]] = str(urlres[cnt])
                cnt += 1

        return res
               
""" def rnb_check(name):
    URL = f"https://nlr.ru/e-case3/sc2.php/web_gak/ss?text={name}x=15&y=17"
    res = []
    res2 = []
    htm = requests.get(URL).text
    soup = BeautifulSoup(htm, "lxml")
    cards = soup.find("div", id="row1textmain").find("div", class_="text").find_all("a", href_="")
    for i in cards:
        if name in str(i.string):
            res.append(i.string)
        res2.append(str(i.string))
    return res2  """

def nnr_check(name):
    URL = f"http://e-heritage.ru/Catalog/FindPerson"
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
    soup = BeautifulSoup(htm, "lxml")
    urlres = soup.find_all("a")

    for j in urlres:
        suburl = str(j["href"])
        suburl = requests.get(f"http://e-heritage.ru{suburl}").text
        sou = BeautifulSoup(suburl, "lxml")
        biores1 = sou.find_all("div", class_="col-4 element_label")
        biores2 = sou.find_all("div", class_="col-6 element_value")
        crdhead = sou.find_all("div", class_="card-header")
        crdbody = sou.find_all("div", class_=re.compile("card-body*"))

        for cnt in range(0, len(biores1)-1):
            res[biores1[cnt].string.replace("\r\n                ", "").replace("    ", "")]\
                = biores2[cnt].string.replace("\r\n                ", "").replace("    ", "")
            
        for crd in range(0, len(crdhead)):
            divchek = " ".join(list(map(lambda x: x.string, crdbody[crd].find_all("div"))))
            lichek = list(map(lambda x: [x.find("a").string.replace("\r\n                ", ""), x.find("a")["href"]] \
                    if x.find("a")["href"][:3] == "htt" else \
                    [x.find("a").string.replace("\r\n                ", ""), "http://e-heritage.ru" + x.find("a")["href"]], \
                      crdbody[crd].find_all("li")))
            if divchek == None or divchek == "":
                crdres[re.search("[а-яА-Я\s]{3,}+", str(crdhead[crd])).group()] = lichek
            else:
                crdres[re.search("[а-яА-Я\s]{3,}+", str(crdhead[crd])).group()] = divchek

        res[biores1[-1].string.replace("\r\n                ", "").replace("    ", "")]\
        = [i.string for i in biores2[-1].find_all("li")]

        return res, crdres

print(nnr_check("Обручев Владимир Афанасьевич"))