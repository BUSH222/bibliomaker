import requests
from bs4 import BeautifulSoup
import re
from helper.bibentry import BibEntry
from helper.handlers import handler
from helper.logger import Logger
from localisation import default


L = default['scrapers']['geoknigasearch']


@handler
def geoknigasearch(person, verbosity=False) -> (None | list[BibEntry]):
    """
    ### Search for a person on the geokniga website.
    ## Args:
        * `person (str)` - name of the person to look up
        * `verbosity (bool, default=False)` - [OPTIONAL] print additional information
    ## Returns:
        * `None` - this person does not exist on the geokniga website
        * `list[BibEntry]` - list of bibliographical entries found on the geokniga website"""
    pages = 1
    surname, name, familyname = person.split()
    URL = f"https://www.geokniga.org/books?field_author={surname}+{name[0]}.{familyname[0]}."

    cnt = 0
    books = []
    finbooks = []

    logger = Logger(verbosity=verbosity)
    logger.log(L['start'])

    r = requests.get(URL).text
    soup = BeautifulSoup(r, "html.parser")
    pages_raw = soup.find(name='li', class_='pager-last last')
    logger.log(L['looking'])

    if pages_raw is not None:
        pages = int(re.search(r"page=(\d*)", str(pages_raw)).group(1))+1
    logger.log(f"{L['pages']}{pages}")
    for i in range(pages):  # Obtain the necessary info
        r = requests.get(f"{URL}&page={i}").text
        soup = BeautifulSoup(r, "html.parser")
        titles = soup.find_all(name='div', class_='book_body_title')
        tomes = soup.find_all(name='div', class_='book_body_izdan_full')
        authors = soup.find_all(name='div', class_='book_body_author')
        publishers = soup.find_all(name='div', class_='book_body_izdat_full')
        cnt += len(titles)
        books.extend(list(zip(titles, tomes, authors, publishers)))
    logger.log(f"{L['books']}{cnt}")
    books = list(map(list, books))

    for i in range(len(books)):  # Cleanup
        temptitles = re.search(r"<a\shref=.*?>(.*?)</a", str(books[i][0]), flags=re.DOTALL)
        temptitles = temptitles.group(1) if temptitles else ''
        temptomes = re.search(r"<div\sclass=.*?>(.*?)</div", str(books[i][1]), flags=re.DOTALL)
        temptomes = temptomes.group(1).strip() if temptomes else ''
        tempauthors = re.findall(r"<cpan class=.*?>(.*?)</cpan>", str(books[i][2]), flags=re.DOTALL)
        tempauthors = tempauthors if tempauthors else []
        temppublishers = re.findall(r"click\(\);\">(.*?)</a>(.*?)</fieldset>", str(books[i][3]), flags=re.DOTALL)
        temppublishers = temppublishers[0] if temppublishers else []
        finbooks.append(BibEntry(authors=' '.join(tempauthors), title=temptitles, physical_desc='',  # No physical desc
                                 source=''.join(temppublishers), tome=temptomes))
    logger.log(L['done'])
    if finbooks == []:
        return None
    return finbooks
