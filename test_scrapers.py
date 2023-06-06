from scrape_papers import PublicationScraper

def test_uob():
    scraper = PublicationScraper()
    url = 'https://research-information.bris.ac.uk/en/persons/arthur-g-richards/publications/'
    df = scraper.scrape_uob_research_info(url)
    scraper.quit()
    print(df)
    assert df.shape==(123,7)

def test_uob_lookup():
    scraper = PublicationScraper()
    uob_url = scraper.lookup_uob('Andrew Conn')
    print(uob_url)
    assert uob_url=='https://research-information.bris.ac.uk/en/persons/andrew-t-conn'

def test_uwe():
    scraper = PublicationScraper()
    url = 'https://uwe-repository.worktribe.com/person/434603/manuel-giuliani/outputs'
    df = scraper.scrape_uwe_repository(url)
    scraper.quit()
    print(df)
    assert df.shape==(47,7)

def test_uwe_lookup():
    scraper = PublicationScraper()
    uwe_url = scraper.lookup_uwe('Manuel Giuliani')
    print(uwe_url)
    assert uwe_url=='https://uwe-repository.worktribe.com/person/434603/manuel-giuliani'

def test_ieee():
    scraper = PublicationScraper()
    url = 'https://ieeexplore.ieee.org/xpl/conhome/9560720/proceeding?isnumber=9560666&sortType=vol-only-seq&refinementName=Affiliation&refinements=Affiliation:University%20of%20Bristol&refinements=Affiliation:Bristol%20Robotics%20Laboratory,%20University%20of%20Bristol,%20Bristol,%20UK&refinements=Affiliation:Bristol%20Robotics%20Laboratory,%20University%20of%20Bristol,%20UK&refinements=Affiliation:Department%20of%20Computer%20Science,%20University%20of%20Bristol,%20Bristol,%20U.K.&refinements=Affiliation:Department%20of%20Engineering%20Mathematics%20and%20Bristol%20Robotics%20Laboratory,%20University%20of%20Bristol,%20Bristol,%20UK&refinements=Affiliation:Department%20of%20Engineering%20Mathematics,%20Bristol%20Robotics%20Laboratory,%20University%20of%20Bristol,%20Bristol,%20U.K.&refinements=Affiliation:Department%20of%20Engineering%20Mathematics,%20Bristol%20Robotics%20Laboratory,%20University%20of%20Bristol,%20U.K.'
    df = scraper.scrape_ieee(url)
    scraper.quit()
    print(df)
    assert df.shape==(7,6)

def test_scholar():
    scraper = PublicationScraper()
    scholar_id = 'pe9bhhAAAAAJ'
    df = scraper.scrape_scholar(scholar_id)
    scraper.quit()
    print(df)
    assert df.shape==(151,7)

def test_scholar_lookup():
    scraper = PublicationScraper()
    scholar_id = scraper.lookup_scholar('Andrew Conn')
    print(scholar_id)
    assert scholar_id=='KdxFB88AAAAJ'

if __name__=='__main__':
    test_uwe()
    test_uob_lookup()
    test_uob()
    test_scholar()
    test_ieee()
