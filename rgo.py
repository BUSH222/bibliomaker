import requests
from bs4 import BeautifulSoup

def rgo_suck(a):
    a = f"https://elib.rgo.ru/simple-search?location=%2F&query={a}&rpp=10&sort_by=score&order=desc"
    req = requests.get(a)
    src = req.text
    soup = BeautifulSoup(src, "lxml")
    try:
        page_p = soup.find("main", class_="main ml-md-5 mr-md-5 mr-xl-0 ml-xl-0").find("p").string
        return page_p
    except:
        return a

ad = rgo_suck("Обручев")
print(ad)
