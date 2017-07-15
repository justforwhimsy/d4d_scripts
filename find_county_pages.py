import facepy as fp
import json
import _mysql
import csv
import requests
import time
import logging
import pprint

token='TOKEN'
graph = fp.GraphAPI(token)
counties_visited = {}

logging.basicConfig(filename='counties.log',  level = logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s')

pp =pprint.PrettyPrinter()
db = _mysql.connect("localhost", 'USER', 'PASSWORD', "DB")

def main():
    with open('us_counties_rest.csv') as f:
        reader = csv.DictReader(f)
        #Iterate over each county in the CSV and collect page results from FB
        for row in reader:
            
            county = row['county']
            logging.debug('County: ' + county)
            count = 0
            # There are multiple counties across the country with the same name, we don't need to search for the same county multiple times
            # if county not in counties_visited:
            if not county_search(county):
                #a dictionary containing search result data.
                results = get_search_results(county)


                #Iterate over each page of results. For each results page, iterate over the FB pages and verify their county before storing them in a database
                for items in results:

                    pages = items['data']
                    for page in pages:
                        page_id, page_name = page['id'], page['name']
                    
                        try:
                            page_category = page['category']
                            logging.debug('Page ID: ' + page_id + " page category: " + page_category + " page name: "+ page_name)
                        
                        except Exception as e:
                            logging.error("failed to get category for " + page_id)
                        try:
                            fb_page=get_page(page_id)
                            try:
                                logging.debug("Collecting Page URL")
                                page_url = fb_page['link']

                            except Exception as e:
                                logging.error("Failed to get url for " + page_name)
                                logging.error(e)
                                page_url = "NULL"

                            if 'location' in fb_page: #if a location does exist on the page, verify what state / county it's in
                                logging.debug('Collecting location')
                                try:
                                    logging.debug('setting page_city and page state')
                                    page_city = fb_page['location']['city']
                                    if ', ' in page_city:
                                        page_city, page_state = page_city.split(', ')
                                    else:
                                        page_state = fb_page['location']['state']
                                    logging.debug('setting verified_county')
                                    verified_county = verify_county_by_state(page_city, page_state)
                                    logging.debug("verified County: " + verified_county)

                                except Exception as e:
                                    logging.error("Failed to get city and/or state for " + page_name)
                                    logging.error(e)
                                    logging.debug('Failed to get city and state for ' + page_id +', gathering county by zip')
                                    try: # If the location did not include a city / state address, look for a postal code
                                        page_zip = fb_page['location']['zip']
                                        logging.debug('page_zip set')
                                        verified_county, page_state = verify_county_by_zip(page_zip)
                                        logging.debug('verified_county and page_state set')
                                    
                                    except Exception as e:
                                        logging.error("Failed to get zip code for " + page_name)
                                        logging.error(e)
                                        page_state = 'NA'
                                        verified_county = 'NULL'
                            
                            insert_page(page_id, page_name, page_url, page_state, verified_county, county)
                            break
                        except Exception as e:
                            logging.error("Failed to get page for " + page_id)
                            logging.error(e)

                        #break out of the loop after running through 4 pages of results. TODO figure out how to limit the pages returned from the getgo
                    count +=1
                    if count == 4:
                        print("Finished collecting pages for " + county)
                        logging.debug("Pages collected for "+ county)
                        time.sleep(30)
                        break

                

            counties_visited[county] = row['state']

def county_search(county):
    try:
        logging.debug('Setting query')
        query = '''Select count(*) from fb_pages where search_county = "%s" ''' % county
        _t = db.query(query)
        result = db.use_result().fetch_row()[0][0]
        if result != '0' :
            return True
        else:
            return False
        logging.debug('county collected')
    except Exception as e:
        logging.error("Error occurred while verifying county already searched for: " + county+ "\n")
        logging.error(e)
        print(e)
        return False
        
    return county
def verify_county_by_state(city, state):
    try:
        logging.debug('Setting query')
        query = '''Select distinct(county) from addresses where state = "%s" and primary_city = "%s"''' % (state, city)
        logging.debug('Query for ' + city + ', ' + state + ': ' + query)
        _t = db.query(query)
        county = db.use_result().fetch_row(1,1)[0]['county'].decode('utf-8')
        logging.debug('county collected')
        logging.debug('True County: ' +county)
    except Exception as e:
        logging.error("Error occurred while searching for county of " +city + ", " + state + "\n")
        logging.error(e)
        county = 'NULL'
        
    return county

def verify_county_by_zip(zip):
    try:
        query = '''Select distinct(county), state from addresses where zip = "%s"''' % zip
        logging.debug('Query: ' + query)
        _t = db.query(query)
        results = db.use_result().fetch_row(1,1)[0]['county'].decode('utf-8')

        logging.debug('Query results: ' + results)
        county, state = results.split(',')

    except Exception as e:
        logging.error("Error occurred while searching for the county by zip code: " + zip +  + "\n")
        logging.error(e)
        #If we couldn't verify the county, we'll want to note that with an empty value in the database
        county = 'NULL'
        state = 'NA'
    return (county,state)

#returns a generator of search results
def get_search_results(term):
    pages = graph.search(term, 'page',True)
    return pages

def get_page_state(page_id):
    state = graph.get(page_id+'?fields=location{state}')['location']['state']
    return state

def get_page(page_id):
    page = graph.get(page_id+"?fields=location,category,link")
    return page

def insert_page(page_id, page_name, page_url, state, verified_county, search_county):
    # user = input('Enter db user: ')
    # password = input('Enter db user password: ')

    query = '''INSERT IGNORE INTO fb_pages (id, page_name, page_url, page_state, verified_county, search_county) VALUES("%s","%s","%s","%s","%s","%s")''' % (page_id, page_name, page_url, state, verified_county, search_county)
    logging.debug("Query: " + query)
    r = db.query(query)
    logging.debug("Query results: " + r)
if __name__ == "__main__":
    main()
