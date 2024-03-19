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
        return URL
               
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


print(rnb_check("пенис"))