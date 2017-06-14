import facepy as fp
import json
import _mysql
import csv
import requests
import time
import logging

token='FACEBOOK TOKEN'
google_key = 'GOOGLE DEVELOPER KEY'
graph = fp.GraphAPI(token)
counties_visited = {}

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.ERROR)

def main():
    with open('us_counties.csv') as f:
        reader = csv.DictReader(f)
        #Iterate over each county in the CSV and collect page results from FB
        for row in reader:
            county = row['county']
            count = 0
            # There are multiple counties across the country with the same name, we don't need to search for the same thing multiple times
            if county not in counties_visited:

                #a dictionary containing search result data.
                results = get_search_results(county)

                #Iterate over each page of results. For each results page, iterate over the FB pages and verify their county before storing them in a database
                for items in results:
                    pages = items['data']
                    for page in pages:
                        page_id, page_name, page_category = page['id'], page['name'],page['category']
                        # page_name =
                        # page_category =
                        try:
                            fb_page=get_page(page_id)
                            try:
                                page_url = fb_page['link']

                            except Exception as e:
                                logger.error("Failed to get url for " + page_name)
                                logger.error(e)
                                # logger.error('page data: ' + fb_page)

                            if 'location' in fb_page: #if a location does exist on the page, verify what state / county it's in
                                try:
                                    page_city = fb_page['location']['city']
                                    if ', ' in page_city:
                                        page_city, page_state = page_city.split(', ')
                                    else:
                                        page_state = fb_page['location']['state']
                                    true_county = get_real_county_by_state(page_city + ',' + page_state)

                                except Exception as e:
                                    logger.error("Failed to get city and/or state for " + page_name)
                                    logger.error(e)
                                    # logger.error(fb_page['location'])

                                    try: # If the location did not include a city / state address, look for a postal code
                                        page_zip = fb_page['location']['zip']
                                        true_county, page_state = get_real_county_by_zip(page_zip)
                                    except Exception as e:
                                        logger.error("Failed to get zip code for " + page_name)
                                        logger.error(e)
                                        # logger.error(fb_page['location'])
                            insert_page(page_id, page_name, page_url, county, page_state, true_county)

                        except Exception as e:
                            logger.error("Failed to get page for " + page_id)
                            logger.error(e)

                        #break out of the loop after running through 4 pages of results. TODO figure out how to limit the pages returned from the getgo
                    count +=1
                    if count == 4:
                        break


                time.sleep(60)

            counties_visited[county] = row['state']


def get_real_county_by_state(address):
    url = 'https://maps.googleapis.com/maps/api/geocode/json?address='
    try:
        r = requests.get(url+str(address)+ "&key=" + google_key)
        r_json = r.json()
        county = r_json['results'][0]['address_components'][1]['short_name'] #should collect the county name. Some places don't have counties, some results don't follow the same format

        state = r_json['results'][0]['formatted_address'].split(', ')[1] #get the second value in the formatted address which will be the state
    except Exception as e:
        logger.error("Error occurred while requesting the url " + url + address + "\n")
        logger.error(e)
    return county

def get_real_county_by_zip(address):
    url = 'https://maps.googleapis.com/maps/api/geocode/json?address='
    try:
        r = requests.get(url+str(address)+ "&key=" + google_key)
        r_json = r.json()
        county = r_json['results'][0]['address_components'][2]['short_name']
        if not('County' in county or 'Parish' in county):
            county = None
        state = r_json['results'][0]['formatted_address'].split(', ')[1] #get the second value in the formatted address which will be the state
    except Exception as e:
        logger.error("Error occurred while requesting the url " + url + address + "\n")
        logger.error(e)
    return (county,state)

def get_county(url, zip_code):
    try:
        r = requests.get(url+zip_code)
    except Exception as e:
        logger.error("Error occurred while requesting the url " + url + zip_code + "\n")
        logger.error(e)
    return r

#returns a generator of search results
def get_search_results(term):
    pages = graph.search(term, 'page',True)

    return pages

def get_page_state(page_id):
    state = graph.get(page_id+'?fields=location{state}')['location']['state']
    print(state)
    return state

def get_page(page_id):
    page = graph.get(page_id)
    return page

def insert_page(page_id, page_name, page_url, search_query, page_state = None, page_county = None):
    # user = input('Enter db user: ')
    # password = input('Enter db user password: ')
    db = _mysql.connect("localhost", 'USER', 'PASSWORD', "DATABASE")
    query = '''INSERT IGNORE INTO fb_pages (id, page_name, page_url, page_state, page_county, search_query) VALUES("%s","%s","%s","%s","%s","%s")''' % (page_id, page_name, page_url, page_state, page_county, search_query)
    db.query(query)

if __name__ == "__main__":
    main()
