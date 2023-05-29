from scrape_papers import PublicationScraper

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

if __name__=='__main__':
    test_ieee()
    test_scholar()
