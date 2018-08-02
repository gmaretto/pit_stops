# Import a library to fetch web content using HTTP requests.
import requests

# Import a library to parse the HTML content of web pages.
from bs4 import BeautifulSoup
# Import a library to handle Regular Expressions
import re


def race_to_tables(url):
    '''[takes an URL on the season page, and returns 
    a list with urls of all files to download from that specific event]

    Arguments:
        url {[string]} -- [ URL on the season page]

    Returns:
        [list] -- [URLs of all files to download from that specific event]
    '''

    content = requests.get(url).content
    soup = BeautifulSoup(content, "html.parser")
    tag = soup.find(
        'div', class_='mosaic-widget-item mosaic-square static-content')
    if tag:
        race_url = tag.a['href']
        race_content = requests.get(race_url).content
        race_soup = BeautifulSoup(race_content, "html.parser")
        table_urls = []
        for row in race_soup.find_all('a', target='_blank'):
            fname = re.findall('/file/(.+)', row.get('href'))
            if fname:
                table_urls.append('https://www.fia.com/file/'+fname[0])
    else:
        table_urls = []
    return table_urls


def do_season(year):
    '''[returns the URL of all events pages for that year]

    Arguments:
        year {[int]} -- [season]

    Returns:
        [list] -- [URL of all events pages for that year]
    '''

    season_url = "https://www.fia.com/events/fia-formula-one-world-championship/season-" + \
        str(year)+"/"+str(year)+"-fia-formula-one-world-championship"
    season_content = requests.get(season_url).content
    season_soup = BeautifulSoup(season_content, "html.parser")
    rows = season_soup.find_all('div', class_='event cell')
    season_url_lst = []
    for row in rows:
        season_url_lst.append("https://www.fia.com"+row.a['href'])
    return season_url_lst


def get_filename_from_cd(cd):
    """
    Get filename from content-disposition
    """
    if not cd:
        return None
    fname = re.findall('filename=(.+)', cd)
    if len(fname) == 0:
        return None
    return fname[0]


def url2pdf(url, year, race):
    '''[takes redirecting URL and saves linked FILE with a prefix in the form YEAR_RACE_]

    Arguments:
        url {[int]} -- [url of file link]
        year {[int]} -- [season]
        race {[int]} -- [number of race in season (starts at 0!)]
    '''

    r = requests.get(url, allow_redirects=True)
    filename = get_filename_from_cd(r.headers.get('content-disposition'))[1:-1]
    #open('raw_data/str(year)/str(race)/'+filename, 'wb').write(r.content)
    print(str(year)+'_'+str(race)+'_'+filename)
    open('raw_data/'+str(year)+'_'+str(race) +
         '_'+filename, 'wb').write(r.content)


if __name__ == "__main__":
    first_season = 2015
    last_season = 2018
    for season in range(first_season, last_season+1):
        season_url_lst = do_season(season)
        for idx, url in enumerate(season_url_lst):
            table_urls = race_to_tables(url)
            if len(table_urls) > 0:
                for url in table_urls:
                    url2pdf(url, season, idx)
