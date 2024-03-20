import requests
from bs4 import BeautifulSoup


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
               
def rnb_check(name):
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
    return res2 


print(rgo_check("Обручев"))