from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.request import urlopen
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("./news-app-da2be-firebase-adminsdk-qjb3c-ccd3331680.json")
firebase_admin.initialize_app(cred)

import nltk

def getCNN():
    driver = webdriver.Chrome()
    driver.get('https://www.cnn.com/politics')

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    bd = soup.find('div', {'class', 'pg-no-rail pg-wrapper'}).find_all('section')

    cnn = []

    for data in bd:
        zn = data.find('div', {'class', 'zn__containers'})
        if zn:
            groups = zn.find_all('div', {'class', 'column'})
            for sets in groups:
                ul = sets.find('ul')
                li = ul.find_all('li')
                for nd in li:
                    art = nd.find('article')
                    finD = art.find('div', {'class', 'cd__content'})
                    a = finD.find('a')
                    url = a.get('href')
                    span = a.find('span')
                    headline = span.getText()
                    d = {"headline" : headline, "url" : 'https://cnn.com' + url}
                    cnn.append(d)
    return cnn

def googleURL():
    def getNouns(headline):
        is_noun = lambda pos: pos[:2] == 'NN'
        tokenized = nltk.word_tokenize(headline)
        nouns = [word for (word, pos) in nltk.pos_tag(tokenized) if is_noun(pos)] 
        return nouns

    # cnn = getCNN()
    # fox = getFox()

    results = []

    for title in cnn:
        headline = title['headline']
        nouns = getNouns(headline)
        preURL = '%2C'.join(nouns)
        preURL.replace('', '%20')
        finURL = "https://news.google.com/search?q={}%20site%3Afoxnews.com%20when%3A7d&hl=en-US&gl=US&ceid=US%3Aen".format(preURL)
        results.append({'fox':finURL, 'cnnH':title['headline'], 'cnnU':title['url']})

    return results
def realFox(results):
    def getFinal(GNurl):
        driver = webdriver.Chrome()
        driver.get(GNurl)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        fdiv = soup.find('div', {'class', 'NiLAwe y6IFtc R7GTQ keNKEd j7vNaf nID9nc'})
        if fdiv:
            h3 = fdiv.find('h3')
            a = h3.find('a')
            url = 'https://news.google.com' + a.get('href')[1:]
            headline = a.getText()
            return headline, url
        return 'None', 'None'

    Lfin = []

    # print(getFinal(results[0]['fox'])))
    for data in results:
        headline, url = getFinal(data['fox'])
        if [headline, url] != ['None', 'None']:
            d = {'cnnHead':data['cnnH'], 'cnnURL':data['cnnU'], 'foxHead':headline, 'foxURL':url}
            Lfin.append(d)
    return Lfin

def writeToDB(allArticles):
    db = firestore.client()
    users_ref = db.collection(u'articles')
    docs = users_ref.stream()

    # for doc in docs:
    #     doc.reference.delete()
        
    i = 1

    for match in allArticles:
        doc_ref = db.collection(u'articles').document(u'document{}'.format(i))
        doc_ref.set({
            u'cnnHead': u'{}'.format(match['cnnHead']),
            u'cnnURL': u'{}'.format(match['cnnURL']),
            u'foxHead': u'{}'.format(match['foxHead']),
            u'foxURL':u'{}'.format(match['foxURL'])
        })
        i += 1


def foxRawData(url):
    driver = webdriver.Chrome()
    driver.get(url)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    fdiv = soup.find('div', {'class', 'page-content'})
    content = fdiv.find('div', {'class', 'article-body'})
    return content
    

def cnnRawData(url):
    driver = webdriver.Chrome()
    driver.get(url)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    fdiv = soup.find('div', {'class', 'pg-right-rail-tall pg-wrapper'})
    article = fdiv.find('article')
    lContainer = article.find('div', {'class', 'l-container'})
    ldiv = lContainer.find('div', {'class', 'pg-rail-tall__body'})
    section = ldiv.find('section')
    lcont2 = section.find('div', {'class', 'l-container'})

    return lcont2


cnn = getCNN()

for article in cnn:
    results = googleURL()
    Lfin = realFox(results)
writeToDB(Lfin)


