import requests
from lxml import html as lxml_html
from bs4 import BeautifulSoup
import logging
import threading
import sys
import argparse
import timeit

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)


#####################################################################################
# Funktionen zum Runterladen Parsen von Inhalt   
#####################################################################################

def download_content(url):
    response = requests.get(url)
    if response.history and ('Location' in response.history[-1].headers):
        '''
            Da Wikipedia unsere Anfrage auf eine neue Seite umleited,
            müssen wir die URL von der neuen Webseite abspeichern.
        '''
        url = response.history[-1].headers['Location']
    return url, response.content, response.status_code


def parse_with_lxml(content):
    '''
        Hier wird der Titel und der erste Satz zu einem Wikipedia-Artikel mit dem lxml Parser geparst.
        Zu beachten ist, dass Wikipedia den ersten Satz im ersten ODER zweiten p-Tag im 
        div-Tag mit dem class-Attribut "mw-parser-output" reinschreibt.
    '''
    soup = BeautifulSoup(content, "lxml")
    try:
        ps = soup.find("div", {'class':'mw-parser-output'}).find_all('p')[:2]
        soup_p = BeautifulSoup(ps[0], 'lxml')
        if len(soup_p.text) < 2:
            sentence = BeautifulSoup(ps[1], 'lxml').text.replace('\n', '')
        else:
            sentence = soup_p.text.replace('\n', '')
    except:
        sentence = "ERROR BS$ LXML"
    return soup.h1.get_text(), sentence


def parse_with_htmlparser(content):
    '''
        Hier wird der Titel und der erste Satz zu einem Wikipedia-Artikel mit dem Standart html.parser geparst.
        Zu beachten ist, dass Wikipedia den ersten Satz im ersten ODER zweiten p-Tag im 
        div-Tag mit dem class-Attribut "mw-parser-output" reinschreibt.
    '''
    soup = BeautifulSoup(content, "html.parser")
    try:
        ps = soup.find("div", {'class':'mw-parser-output'}).find_all('p')[:2]
        soup_p = BeautifulSoup(ps[0], 'html.parser')
        if len(soup_p.text) < 2:
            sentence = BeautifulSoup(ps[1], 'html.parser').text.replace('\n', '')
        else:
            sentence = soup_p.text.replace('\n', '')
    except:
        sentence = "ERROR BS4 HTML"
    return soup.h1.get_text(), sentence


def parse_with_html5lib(content):
    '''
        Hier wird der Titel und der erste Satz zu einem Wikipedia-Artikel mit dem html5lib Parser geparst.
        Zu beachten ist, dass Wikipedia den ersten Satz im ersten ODER zweiten p-Tag im 
        div-Tag mit dem class-Attribut "mw-parser-output" reinschreibt.
    '''
    soup = BeautifulSoup(content, "html5lib")
    try:
        ps = soup.find("div", {'class':'mw-parser-output'}).find_all('p')[:2]
        soup_p = BeautifulSoup(ps[0], 'html5lib')
        if len(soup_p.text) < 2:
            sentence = BeautifulSoup(ps[1], 'html5lib').text.replace('\n', '')
        else:
            sentence = soup_p.text.replace('\n', '')
    except:
        sentence = "ERROR BS4 HTML5"
    return soup.h1.get_text(), sentence


def parse_only_with_lxml(content):
    '''
        Hier wird der Titel und der erste Satz zu einem Wikipedia-Artikel mit dem lxml Parser geparst. 
        Dabei wird aber nicht BeautifulSoup verwendet.
        Zu beachten ist, dass Wikipedia den ersten Satz im ersten ODER zweiten p-Tag im 
        div-Tag mit dem class-Attribut "mw-parser-output" reinschreibt.
    '''
    tree = lxml_html.fromstring(content)
    try:
        sentence = tree.xpath("//div[@class='mw-parser-output']/p")[0].text_content().replace('\n', '')
        if len(sentence) < 2:
            sentence = tree.xpath("//div[@class='mw-parser-output']/p")[0].text_content().replace('\n', '')
    except:
        sentence = 'ERROR XPATH'
    return tree.xpath("//h1")[0].text_content(), sentence


#####################################################################################
# Funktionen zum Crawlen  
#####################################################################################

def run_crawl(parser, urls, id=0):
    logger.info(f"Prozess {id} gestartet! Parser: {parser}, URLs: {len(urls)}")

    for url in urls:
        logger.debug(f"Aktuelle URL: {url}")
        
        if parser == 'lxml':
            parse_func = parse_with_lxml
        elif parser == 'html':
            parse_func = parse_with_htmlparser
        elif parser == 'html5.lib':
            parse_func = parse_with_html5lib
        else:
            parse_func = parse_only_with_lxml
 
        url, content, code = download_content(url)
        if int(code) != 200:
            with open("requests_scraped_data.txt", "a") as f:
                f.write(f"URL: {url}, Code: {code}\n")
        title, sentence = parse_func(content)

        with open("requests_scraped_data.txt", "a") as f:
            f.write(f"URL: {url}, Code: {code}, Titel: {title}, Satz: {sentence}\n")


#####################################################################################
# Funktionen fürs Multi Threading Crawlen 
#####################################################################################
def call_with_threading(n_threads, parser, urls):
    threads = []
 
    thread_url_amount = int(len(urls)/n_threads)

    for i in range(0, n_threads):
        process_urls = urls[:thread_url_amount]

        t = threading.Thread(target=run_crawl, args=[parser, process_urls, i])
        threads.append(t)
        t.start()
 
    for t in threads:
        t.join()


#####################################################################################
# Funktionen um URL Liste zu bekommen
#####################################################################################
def get_urls():
    return ["https://de.wikipedia.org/wiki/Spezial:Zuf%C3%A4llige_Seite" for i in range(1000)]



#####################################################################################
# Main Funktion
#####################################################################################
def main(n_threads, parser):
    if n_threads == 1:
        run_crawl(parser, get_urls())
    else:
        call_with_threading(n_threads, parser, get_urls())


#####################################################################################
# Configuration für Main Funktion
#####################################################################################
if __name__ == "__main__":
    with open('requests_results.csv', 'w') as f:
        f.write('n_threads,lxml,html,html5,only_lxml\n')

    for n_threads in [20]:
        start_lxml = timeit.default_timer()
        main(n_threads, 'lxml')
        end_lxml = timeit.default_timer()

        start_html = timeit.default_timer()
        main(n_threads, 'html')
        end_html = timeit.default_timer()

        start_html5 = timeit.default_timer()
        main(n_threads, 'html5.lib')
        end_html5 = timeit.default_timer()

        start_only_lxml = timeit.default_timer()
        main(n_threads, 'only_lxml')
        end_only_lxml = timeit.default_timer()

        with open('requests_results.csv', 'a') as f:
            f.write(f'{n_threads},{end_lxml-start_lxml},{end_html-start_html},{end_html5-start_html5},{end_only_lxml-start_only_lxml}\n')
