from bs4 import BeautifulSoup
import sqlite3
import requests
import time

# --------

# Все коменты - это финальные нужные мне данные

# --------


class UsersDB:
    name = 'meduza.db'

    _db_connection = None
    _db_cur = None

    def __init__(self):
        self._db_connection = sqlite3.connect(self.name)
        self._db_cur = self._db_connection.cursor()

    def query(self, query):
        self._db_cur.execute(query)
        self._db_connection.commit()
        return

    def fetch(self, query):
        return self._db_cur.execute(query).fetchall()

    def save(self):
        self._db_connection.commit()

    def __del__(self):
        self._db_connection.close()


class Article:
    url = ""
    title1 = ""
    title2 = ""
    leadText = []
    allText = []
    materialNote = ""
    allMedia = []

    def __init__(self, title1, title2, url, leadText, allText, materialNote, allMedia):
        self.title1 = title1
        self.title2 = title2
        self.url = url
        self.leadText = leadText
        self.allText = allText
        self.materialNote = materialNote
        self.allMedia = allMedia


url = 'https://meduza.io/feature/2017/05/26/kakovo-eto-kogda-v-tebya-popadaet-molniya'
html = requests.get(url).text
soup = BeautifulSoup(html, "lxml")

title1 = soup.find("span", {'class': 'MediaMaterialHeader-first'}).text
try:
    title2 = soup.find("span", {'class': 'MediaMaterialHeader-second'}).text
except AttributeError:
    print('TITLE 2 - NONE!!!!')

# print(title1, title2)

div = soup.find('div', {'class': 'MediaMaterial-materialContent'})
try:
    mainMaterialImage = div.find('div', {'class': 'MainMaterialImage-image'}).find('img').get('src')
except AttributeError:
    pass

leadContent = div.find('div', {'class': 'Lead'}).find_all('p')
leadText = []
allText = []
for i in leadContent:
    leadText.append(i.text)

bodyContent = div.find('div', {'class': 'Body'}).find_all('p')
for i in bodyContent:
    allText.append(i.text)

materialNote = div.find('div', {'class': 'MaterialNote'}).find('strong').text

# print(leadText)
# print(allText)
# print(materialNote)

imgContent = div.find('div', {'class': 'MaterialContent'})
img = imgContent.find_all('img')

allMedia = []

for i in img:
    oneImg = i.get('src')
    allMedia.append(oneImg)
video = imgContent.find_all('iframe')
for i in video:
    allMedia.append(i.get('src'))
try:
    allMedia.append(mainMaterialImage)
except NameError:
    pass


# print(allMedia)


def createArt():
    db = UsersDB()
    db.query(
        'CREATE TABLE article(id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, title1 TEXT, title2 TEXT ,link TEXT, leadText TEXT, bodyText TEXT, noter TEXT);')


def createMedia():
    db = UsersDB()
    db.query(
        'CREATE TABLE Media(id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, linkToMedia TEXT, articleID INTEGER);')


def addArticle(title1, title2, url, leadText, allText, materialNote, allMedia):
    db = UsersDB()
    t = ''

    for i in leadText:
        t += i
        t += ' '
    if len(leadText) == 0:
        t = "None"
    t2 = ''
    for i in allText:
        t2 += i
        t2 += ' '
    if len(allText) == 0:
        t2 = "None"
    db.query(
        'INSERT INTO article(title1, title2 ,link, leadText, bodyText, noter) values(\'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\')' % (
            title1, title2, url, t, t2, materialNote))
    prId = db.fetch("Select id from article order by id DESC limit 1")
    for media in allMedia:
        db.query('INSERT INTO Media(linkToMedia, articleID) values(\'%s\', %d)' % (media, prId[0][0]))


addArticle(title1, title2, url, leadText, allText, materialNote, allMedia)

clas = Article(title1, title2, url, leadText, allText, materialNote, allMedia)
