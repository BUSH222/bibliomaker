import requests
from bs4 import BeautifulSoup

def org_suck(a):
    req = requests.get("https://elib.rgo.ru/simple-search?location=%2F&query=Русаков&rpp=10&sort_by=score&order=desc")
    src = req.text
    soup = BeautifulSoup(src, "lxml")
    title = soup.title.string
    page_p = soup.find("main", class_="main ml-md-5 mr-md-5 mr-xl-0 ml-xl-0").find("p").string
    if page_p == "Поиск не дал результатов ":
        print("Нет данных")


org_suck("Обручев")
