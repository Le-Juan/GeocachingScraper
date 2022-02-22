import re
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

#chrome_options = Options()

opt = webdriver.ChromeOptions()
opt.add_argument("--window-size=1366,768");
opt.add_argument("--no-sandbox");
opt.add_argument("--disable-gpu");
opt.add_argument("--enable-javascript");
opt.add_argument("disable-infobars");
opt.add_argument("--disable-infobars");
opt.add_argument("--single-process");
opt.add_argument("--disable-extensions");
opt.add_argument("--disable-dev-shm-usage");
opt.add_argument("--headless");
opt.add_argument("enable-automation");
opt.add_argument("--disable-browser-side-navigation");

driver = webdriver.Chrome(executable_path='C:\sources\webdriver\chromedriver.exe', options=opt)

driver.get('https://www.geocaching.com/account/signin?returnUrl=https%3A%2F%2Fwww.geocaching.com%2Fseek%2Fnearest.aspx')

driver.find_element_by_id("CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll").click()
driver.find_element_by_id("UsernameOrEmail").send_keys('ADD YOUR OWN USERNAME OR EMAIL')
driver.find_element_by_id("Password").send_keys("ADD YOUR OWN PASSWORD")
driver.find_element_by_id("SignIn").click()

webPaginas = ['https://www.geocaching.com/seek/nearest.aspx?country_id=141&as=1&ex=0&cFilter=9a79e6ce-3344-409c-bbe9-496530baf758&children=n',
              'https://www.geocaching.com/seek/nearest.aspx?country_id=79&as=1&ex=0&cFilter=9a79e6ce-3344-409c-bbe9-496530baf758&children=n',
              'https://www.geocaching.com/seek/nearest.aspx?country_id=4&as=1&ex=0&cFilter=9a79e6ce-3344-409c-bbe9-496530baf758&children=n',
              'https://www.geocaching.com/seek/nearest.aspx?country_id=73&as=1&ex=0&cFilter=9a79e6ce-3344-409c-bbe9-496530baf758&children=n',
              'https://www.geocaching.com/seek/nearest.aspx?country_id=8&as=1&ex=0&cFilter=9a79e6ce-3344-409c-bbe9-496530baf758&children=n',
              'https://www.geocaching.com/seek/nearest.aspx?country_id=11&as=1&ex=0&cFilter=9a79e6ce-3344-409c-bbe9-496530baf758&children=n',
              ]

for position in webPaginas:
    links = []
    GeoCodes = []
    coordinaten = []

    URLNummer = 0
    driver.get(position)
    content = driver.page_source

    soup = BeautifulSoup(content, features="html.parser")
    for body in soup.findAll('div', {'class': 'span-20 last'}):
        numberPages = body.find('div', {'id': 'ctl00_ContentBody_ResultsPanel'})
        if numberPages is not None:
            numberPagesEnd= numberPages.find('table', {'class': 'NoBottomSpacing'}).findAll('b')
        huidigePagina = 1
        totalePagina = int(numberPagesEnd[2].text)

        while huidigePagina <= totalePagina:
            huidigePagina = huidigePagina + 1
            if huidigePagina > totalePagina:
                break
            for row in soup.findAll('tr', {"class":["SolidRow Data BorderTop", "BeginnerRow Data BorderTop", "AlternatingRow Data BorderTop"]}):
                checkbox = row.find('td').input
                if checkbox is not None:
                    cacheCodeLocator = row.find("td", {"class": "Merge"}).findNextSibling("td").text
                    #print(cacheCodeLocator)
                    if "GC" in cacheCodeLocator:
                        b = cacheCodeLocator
                        c = re.findall("GC.....", b)
                        print(c)
                        if len(c) == 0:
                            d = re.findall("GC....", b)
                            print(d)
                            GeoCodes.append(d[len(d)-1])
                        else:
                            GeoCodes.append(c[len(c)-1])

                    cachePage = row.find("td", {"class": "Merge"}).findNextSibling("td").a['href']
                    if cachePage is not None:
                        driver.get(str(cachePage))
                        coordcontent = driver.page_source
                        coordinatenpagina = BeautifulSoup(coordcontent, features="html.parser")
                        if coordinatenpagina is None:
                            coordinaat = ''
                            coordinaten.append(coordinaat)
                        else:
                            coordinaat = coordinatenpagina.find('div', class_='span-9').p.span.strong.span.text
                            coordinaten.append(coordinaat)                            
                        driver.back()
                    links.append(cachePage)
                    #driver.get(str(Cachepage))

            if numberPages is not None:
                nextPage = len(soup.find('div', {'id': 'ctl00_ContentBody_ResultsPanel'}).find('table', {'class': 'NoBottomSpacing'}).findAll('a'))
            print(nextPage)
            driver.find_element_by_xpath("//*[@id='ctl00_ContentBody_ResultsPanel']/table[1]/tbody/tr/td[2]/a[{}]".format(nextPage)).click()

            content2 = driver.page_source
            soup = BeautifulSoup(content2, features="html.parser")
            body2 = soup.find('div', {'class': 'span-20 last'})
            numberPages = body2.find('div', {'id': 'ctl00_ContentBody_ResultsPanel'}).find('table', {'class': 'NoBottomSpacing'}).findAll('b')
            totalePagina = int(numberPages[2].text)
            print(huidigePagina, totalePagina)
            df = pd.DataFrame({'GeoCodes': GeoCodes, 'links': links, 'coordinaten': coordinaten})
            df.to_csv('C_And_C_poging_{}.csv'.format(URLNummer), index=True, encoding='utf-8')
        URLNummer = URLNummer + 1

driver.close()
