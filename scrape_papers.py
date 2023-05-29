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

    def scrape_uob_research_info_url(self, url):
        print(f'Scraping {url}')
        resp = requests.get(url, timeout=60)
        soup = BeautifulSoup(resp.text, 'html.parser')
        paper_tags = soup.find_all(class_='result-container')
        data_dict = {'title': [p.h3.text for p in paper_tags],
                    'uob_detail_url': [p.a.get('href') for p in paper_tags],
                    'uob_date_str': [p.findAll(class_='date')[0].text for p in paper_tags]}
        df = pd.DataFrame(data=data_dict)
        df['source_url'] = url
        df['date'] = pd.to_datetime(df['uob_date_str'], format='mixed')
        df['name'] = soup.h1.text
        return df

    def scrape_uob_research_info_author(self, author_id):
        df = pd.DataFrame()
        pg = 0
        while True:
            url = f'https://research-information.bris.ac.uk/en/persons/{author_id}/publications/?page={pg}'
            new_df = self.scrape_uob_research_info_url(url)
            if len(new_df)>0:
                df = pd.concat([df, new_df])
                pg += 1
            else:
                break
        df['uob_author'] = author_id
        df = df.reset_index()
        return df

    def scrape_uwe_repository_url(self, url):
        print(f'Scraping {url}')
        resp = requests.get(url, timeout=60)
        soup = BeautifulSoup(resp.text, 'html.parser')
        paper_tags = soup.find_all('blockquote')
        data_dict = {'title': [p.strong.text for p in paper_tags],
                    'uwe_year_str': [p.small.text[1:5] for p in paper_tags],
                    'uwe_detail_link': [p.a.get('href') for p in paper_tags]}
        df = pd.DataFrame(data=data_dict)
        df['source_url'] = url
        df['date'] = pd.to_datetime(df['uwe_year_str'], format='mixed', errors='ignore')
        df['author_name'] = soup.title.text.strip()
        return df

    def scrape_uwe_repository_author(self, author_id):
        df = pd.DataFrame()
        pg = 1
        while True:
            url = f'https://uwe-repository.worktribe.com/person/{author_id}/user/outputs?page={pg}'
            new_df = self.scrape_uwe_repository_url(url)
            if len(new_df)>0:
                df = pd.concat([df, new_df])
                pg += 1
            else:
                break
        df['uwe_author'] = author_id
        df = df.reset_index()
        return df

    def startdriver(self):
        # start by defining the options
        options = webdriver.ChromeOptions()
        options.headless = True # it's more scalable to work in headless mode
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
        if self.driver is None:
            self.startdriver()
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
        if self.driver is None:
            self.startdriver()
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

    def scrape_ieee(self, url):
        if self.driver is None:
            self.startdriver()
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
    parser = ArgumentParser(prog='test_scrapers',
                            description='cmmand line utility for publication scraping')
    parser.add_argument('-s','--scholar',help='User ID on Google Scholar')
    parser.add_argument('-i','--ieee',help='IEEExplore URL')
    parser.add_argument('-b','--bristol',help='UoB person identifier')
    parser.add_argument('-o','--orcid',help='Individual ORCID')
    args = parser.parse_args()
    scraper = PublicationScraper()
    if args.scholar:
        res = scraper.scrape_scholar(args.scholar)
        scraper.driver.quit()
        res.to_csv('scholar_data.csv')
