import time
from argparse import ArgumentParser
import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

class PublicationScraper:
    "Tools for getting bibliographical information from internet sources"

    def __init__(self):
        self.driver = None

    def scrape_uob_research_info(self, url, extra_pages=True):
        """Search for publications on a UWE repository URL
        Will traverse multiple pages unless extra_pages=False"""
        print(f'Scraping {url}')
        resp = requests.get(url, timeout=60)
        soup = BeautifulSoup(resp.text, 'html.parser')
        author_name = soup.h1.text
        paper_tags = soup.find_all(class_='result-container')
        data_dict = {'title': [p.h3.text for p in paper_tags],
                    'uob_detail_url': [p.a.get('href') for p in paper_tags],
                    'uob_date_str': [p.findAll(class_='date')[0].text for p in paper_tags]}
        df = pd.DataFrame(data=data_dict)
        df['source_url'] = url
        if extra_pages:
            pg = 1
            while True:
                pg_url = f'{url}?page={pg}'
                print(f'Scraping {pg_url}')
                resp = requests.get(pg_url, timeout=60)
                soup = BeautifulSoup(resp.text, 'html.parser')
                paper_tags = soup.find_all(class_='result-container')
                if paper_tags:
                    data_dict = {'title': [p.h3.text for p in paper_tags],
                        'uob_detail_url': [p.a.get('href') for p in paper_tags],
                        'uob_date_str': [p.findAll(class_='date')[0].text for p in paper_tags]}
                    pg_df = pd.DataFrame(data=data_dict)
                    pg_df['source_url'] = pg_url
                    df = pd.concat([df, pg_df])
                    pg += 1
                else:
                    break
        df['date'] = pd.to_datetime(df['uob_date_str'], format='mixed')
        df['uob_author'] = author_name
        df = df.reset_index()
        return df

    def lookup_uob(self, search_name):
        "Search for individual by name on UoB research-information website.  Returns profile URL of top matching result."
        search_term = search_name.lower().replace(' ','+')
        url = f'https://research-information.bris.ac.uk/en/persons/?search={search_term}'
        print(f'Checking {url}')
        resp = requests.get(url, timeout=60)
        soup = BeautifulSoup(resp.text, 'html.parser')
        top_result = soup.find(class_='result-container')
        try:
            result_url = top_result.a.get("href")
        except AttributeError:
            result_url = None
        return result_url

    def scrape_uwe_repository(self, url, extra_pages=True):
        """Search for publications on a UWE repository URL
        Will traverse multiple pages unless extra_pages=False"""
        print(f'Scraping {url}')
        resp = requests.get(url, timeout=60)
        soup = BeautifulSoup(resp.text, 'html.parser')
        paper_tags = soup.find_all('blockquote')
        data_dict = {'title': [p.strong.text for p in paper_tags],
                    'uwe_year_str': [p.small.text[1:5] for p in paper_tags],
                    'uwe_detail_link': [p.a.get('href') for p in paper_tags]}
        df = pd.DataFrame(data=data_dict)
        df['source_url'] = url
        author_name = soup.title.text.strip()
        if extra_pages:
            pg = 2
            while True:
                pg_url = f'{url}?page={pg}'
                print(f'Scraping {pg_url}')
                resp = requests.get(pg_url, timeout=60)
                soup = BeautifulSoup(resp.text, 'html.parser')
                paper_tags = soup.find_all('blockquote')
                if paper_tags:
                    data_dict = {'title': [p.strong.text for p in paper_tags],
                                 'uwe_year_str': [p.small.text[1:5] for p in paper_tags],
                                 'uwe_detail_link': [p.a.get('href') for p in paper_tags]}
                    pg_df = pd.DataFrame(data=data_dict)
                    pg_df['source_url'] = pg_url
                    df = pd.concat([df, pg_df])
                    pg += 1
                else:
                    break
        df['date'] = pd.to_datetime(df['uwe_year_str'], format='mixed', errors='ignore')
        df['uwe_author'] = author_name
        df = df.reset_index()
        return df

    def lookup_uwe(self, search_name):
        "Search for an individual by name on UWE repository.  Returns URL of top matching profile."
        search_term = search_name.lower().replace(' ','+')
        url = f'https://uwe-repository.worktribe.com/search/person/people?criteria={search_term}'
        print(f'Checking {url}')
        resp = requests.get(url, timeout=60)
        soup = BeautifulSoup(resp.text, 'html.parser')
        top_result = soup.find(class_="content")
        result_url = top_result.find('a').get("href")
        return result_url

    def start_driver(self):
        "Start a Selenium web driver for web scraping"
        # start by defining the options
        options = webdriver.ChromeOptions()
        options.add_argument('--headless') # it's more scalable to work in headless mode
        # normally, selenium waits for all resources to download
        # we don't need it as the page also populated with the running javascript code.
        options.page_load_strategy = 'none'
        # this returns the path web driver downloaded
        chrome_path = ChromeDriverManager().install()
        chrome_service = Service(chrome_path)
        # pass the defined options and service objects to initialize the web driver
        self.driver = Chrome(options=options, service=chrome_service)
        self.driver.implicitly_wait(5)

    def quit(self):
        "Close down any hanging web connections"
        if self.driver:
            self.driver.quit()

    def scrape_orcid(self, orcid):
        "Return paper details for an individual via ORCID"
        if self.driver is None:
            self.start_driver()
        url = f'https://orcid.org/{orcid}/print'
        print(f'Scraping {url}')
        self.driver.get(url)
        time.sleep(10)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        work_list = soup.find('ul', class_='workspace-publications')
        paper_tags = work_list.find_all(class_='work-list-container')
        data_dict = {'title': [p.find(id="work.title").text for p in paper_tags],
                    'orcid_year_str': [p.find(class_='info-detail').span.text for p in paper_tags],
                    'doi_url': [p.find_all('a', class_="ng-binding")[-1].get('href') if p.find_all('a', class_="ng-binding") else '' for p in paper_tags]}
        df = pd.DataFrame(data=data_dict)
        df['source_url'] = url
        df['date'] = pd.to_datetime(df['orcid_year_str'], format='mixed', errors='ignore')
        df['author'] = soup.h2.text.strip()
        df['orcid'] = orcid
        return df

    def scrape_scholar(self, scholar_id):
        "Return paper details for an individual profile on Google Scholar"
        if self.driver is None:
            self.start_driver()
        url = f'https://scholar.google.com/citations?hl=en&user={scholar_id}'
        print(f'Scraping {url}')
        self.driver.get(url)
        time.sleep(10)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        paper_tags = soup.find_all('tr',class_='gsc_a_tr')
        num_tags = len(paper_tags)
        # click "show more" as long as getting more papers
        while True:
            print(f'Got {num_tags} entries.  Clicking MORE...')
            more_button = self.driver.find_element(By.ID, "gsc_bpf_more")
            self.driver.execute_script("arguments[0].click();", more_button)
            time.sleep(10)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            paper_tags = soup.find_all('tr',class_='gsc_a_tr')
            if len(paper_tags)>num_tags:
                num_tags = len(paper_tags)
            else:
                print(f'{num_tags} is all we''re going to get')
                break
        data_dict = {'title': [p.a.text for p in paper_tags],
                    'scholar_year_str': [p.find(class_='gsc_a_y').text for p in paper_tags],
                    'scholar_url': ['https://scholar.google.com'+p.a.get('href') for p in paper_tags]}
        df = pd.DataFrame(data=data_dict)
        df['source_url'] = url
        df['date'] = pd.to_datetime(df['scholar_year_str'], format='mixed', errors='ignore')
        df['author'] = soup.find_all(id='gsc_prf_in')[0].text.strip()
        df['scholar_id'] = scholar_id
        return df

    def lookup_scholar(self, search_name):
        "Look up Google Scholar ID of an individual by name"
        if self.driver is None:
            self.start_driver()
        search_term = search_name.lower().replace(' ','+')
        url=f'https://scholar.google.com/citations?view_op=search_authors&hl=en&mauthors={search_term}+bristol&btnG='
        print(f'Searching {url}')
        self.driver.get(url)
        time.sleep(10)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        h3_tag = soup.find('h3')
        target_url = h3_tag.find('a').get('href')
        split_it = target_url.split('=')
        user_id = split_it[-1]
        return user_id

    def scrape_ieee(self, url):
        "Retrieve paper details from a page on IEEExplore"
        if self.driver is None:
            self.start_driver()
        print(f'Scraping {url}')
        self.driver.get(url)
        time.sleep(10)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        #print(soup)
        paper_tags = soup.find_all(class_='result-item')
        #print(paper_tags)
        def get_ieee_year(paper_tag):
            desc = paper_tag.find_all(class_='description')[0].text
            ix = desc.find('Year: ')
            year_str = desc[ix+6:ix+10]
            return year_str
        data_dict = {'title': [p.find('h2').text for p in paper_tags],
                    'ieee_url': ['https://ieeexplore.ieee.org/'+p.find('a').get('href') for p in paper_tags],
                    'author_list': [p.find(class_='author').text.split(';') for p in paper_tags],
                    'ieee_year_str': [get_ieee_year(p) for p in paper_tags]}
        df = pd.DataFrame(data=data_dict)
        df['source_url'] = url
        df['date'] = pd.to_datetime(df['ieee_year_str'], format='mixed', errors='ignore')
        return df

if __name__=='__main__':
    parser = ArgumentParser(prog='scrape_papers',
                            description='command line utility for publication scraping')
    parser.add_argument('-s','--scholar',help='User ID on Google Scholar')
    parser.add_argument('-i','--ieee',help='IEEExplore URL')
    parser.add_argument('-b','--bristol',help='UoB person name')
    parser.add_argument('-w','--uwe',help='UWE person name')
    parser.add_argument('-o','--orcid',help='Individual ORCID')
    parser.add_argument('-q','--query',help='Look up author links by name')
    args = parser.parse_args()
    scraper = PublicationScraper()
    res = None
    if args.scholar:
        res = scraper.scrape_scholar(args.scholar)
        scraper.quit()
        res.to_csv('scholar_data.csv')
    elif args.bristol:
        test_url = scraper.lookup_uob(args.bristol)
        res = scraper.scrape_uob_research_info(test_url+'/publications/')
        scraper.quit()
        res.to_csv('bristol_data.csv')
    elif args.uwe:
        test_url = scraper.lookup_uwe(args.uwe)
        res = scraper.scrape_uwe_repository(test_url+'/outputs')
        scraper.quit()
        res.to_csv('uwe_data.csv')
    elif args.query:
        test_scholar_id = scraper.lookup_scholar(args.query)
        print(f'Scholar ID is {test_scholar_id}')
        bristol_url = scraper.lookup_uob(args.query)
        print(f'Bristol profile URL is {bristol_url}')
        uwe_url = scraper.lookup_uwe(args.query)
        print(f'UWE profile URL is {uwe_url}')
