from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.request import urlopen
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("./news-app-da2be-firebase-adminsdk-qjb3c-ccd3331680.json")
firebase_admin.initialize_app(cred)

import nltk
# nltk.download('all')

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
                    print(d['url'])
                    if d['url'][15] == '/':
                        print(d['url'])
                        cnn.append(d)
    return cnn

def getFox():
    fox = []
    html = urlopen('http://www.foxnews.com/politics')
    bs = BeautifulSoup(html, "html.parser")
    titles = bs.find_all(['h2','h4'])
    for data in titles:
        atag = data.find('a')
        headline = atag.getText()
        url = atag.get('href')
        d = {"headline" : headline,
                "url" : url}
        fox.append(d)
    return fox

def getNouns(headline):
    is_noun = lambda pos: pos[:2] == 'NN'
    tokenized = nltk.word_tokenize(headline)
    nouns = [word for (word, pos) in nltk.pos_tag(tokenized) if is_noun(pos)] 
    return nouns

cnn = getCNN()
fox = getFox()

results = []

for title in cnn:
    headline = title['headline']
    nouns = getNouns(headline)
    preURL = '%2C'.join(nouns)
    preURL.replace('', '%20')
    finURL = "https://news.google.com/search?q={}%20site%3Afoxnews.com%20when%3A7d&hl=en-US&gl=US&ceid=US%3Aen".format(preURL)
    results.append({'fox':finURL, 'cnnH':title['headline'], 'cnnU':title['url']})

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

def foxRawData(url):
    driver = webdriver.Chrome()
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    try:
        fdiv = soup.find('div', {'class', 'page-content'})
        content = fdiv.find('div', {'class', 'article-body'})
        return content
    except:
        return 'NULL'
        
    

def cnnRawData(url):
    driver = webdriver.Chrome()
    driver.get(url)
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        fdiv = soup.find('div', {'class', 'pg-right-rail-tall'})
        article = fdiv.find('article')
        lContainer = article.find('div', {'class', 'l-container'})
        ldiv = lContainer.find('div', {'class', 'pg-rail-tall__body'})
        section = ldiv.find('section')
        lcont2 = section.find('div', {'class', 'l-container'})

        return lcont2
    except:
        return 'ERROR'


Lfin = []

# print(getFinal(results[0]['fox'])))
print(results)
for data in results:
    headline, url = getFinal(data['fox'])
    if [headline, url] != ['None', 'None']:
        foxCont = foxRawData(url)
        if foxCont != 'NULL':
            cnnCont = cnnRawData(data['cnnU'])
            d = {'cnnHead':data['cnnH'], 'cnnURL':data['cnnU'], 'cnnCont':cnnCont, 'foxHead':headline, 'foxURL':url, 'foxCont':foxCont}
            Lfin.append(d)


print(Lfin)

def writeToDB(allArticles):
    db = firestore.client()
    users_ref = db.collection(u'articles')
    docs = users_ref.stream()

    for doc in docs:
        doc.reference.delete()
        
    i = 1
    for match in allArticles:
        doc_ref = db.collection(u'articles').document(u'document{}'.format(i))
        doc_ref.set({
            u'cnnHead': u'{}'.format(match['cnnHead']),
            u'cnnURL': u'{}'.format(match['cnnURL']),
            u'foxHead': u'{}'.format(match['foxHead']),
            u'foxURL':u'{}'.format(match['foxURL']),
            u'cnnCont': u'{}'.format(match['cnnCont']),
            u'foxCont':u'{}'.format(match['foxCont'])
        })
        i += 1
        

writeToDB(Lfin)



