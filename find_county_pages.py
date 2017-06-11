import facepy as fp
import pprint
import json
import _mysql
import csv
import time
import requests
token='EAACEdEose0cBAPsl349gnWVwyZCt22ZBvmFj9aMyGVmIiVWCXLe7xQ5AYFFO6eGYcryZBZAUKDrUSq2DHi9gTiW3mJhzQirGEmpoqQM5MPVfIvS0AP3BUeoPCBWsd9kBDAdbHHePZBSaZCNOZA92jE1qbp6g3TK09UqoEhfQihTmBU9FpdBkZBZCtAs9YBuiLqCUZD'
pp = pprint.PrettyPrinter()
graph = fp.GraphAPI(token)
counties_visited = {}
def main():
    with open('us_counties.csv') as f:
        reader = csv.DictReader(f)
        count = 0
        #Iterate over each county in the CSV and collect page results from FB
        for row in reader: 
            county = row['county']

            # There are multiple counties across the country with the same name, we don't need to search for the same thing multiple times
            if county not in counties_visited:

                #a dictionary containing search result data
                results = get_search_results(county)

                #Each item in the list contains a dictiory object containing information on the page.
                #Iterate over each page of results. For each results page, iterate over the FB pages and compare their states
                count=0
                for items in results:
                    pages = items['data']
                    for page in pages:
                        # print(page)
                        page_id = page['id']
                        page_name = page['name']
                        page_category = page['category']
                #         page_url = "get page url"
                #       #TODO Get the state for the page and verify it matches the county we are looking for.
                        try:
                            fb_page=get_page(page_id)
                            # print(fb_page)
                            try:
                                page_url = fb_page['link']
         
                            except Exception as e:
                                print("Failed to get url for " + page_name)
                                print(e)
                            
                            if 'location' in fb_page:
                                print(fb_page['location'])
                                try:
                                    page_state = fb_page['location']['state']
                                    page_city = fb_page['location']['city']
                                    true_county = get_real_county_by_state(page_city + ',' + page_state)
                                except Exception as e:
                                    print("Failed to get city and/or state for " + page_name)
                                    print(e)

                                else:
                                    try:
                                        page_zip = fb_page['location']['zip']
                                        true_county, page_state = get_real_county_by_zip(page_zip)
                                    except Exception as e:
                                        print("Failed to get zip code for " + page_name)
                                        print(e)        

                            # print(true_county + " : " + page_state)
                        except Exception as e:
                            print("Failed to get page for " + page_id)
                            print(e)
                        
                #     count +=1
                #     #break out of the loop after running through 4 pages of results. TODO figure out how to limit the pages returned from the getgo
                #     if count == 4:
                #         break
                    break
                break
                time.sleep(120)
            break
            counties_visited[county] = row['state']
    print(count)


def get_real_county_by_state(address):
    url = 'http://maps.googleapis.com/maps/api/geocode/json?address='
    try:
        r = requests.get(url+str(address))
        r_json = r.json()
        print(r_json)
        county = r_json['results'][0]['address_components'][1]['long_name']
        state = r_json['results'][0]['address_components'][2]['short_name']
    except Exception as e:
        print("Error occurred while requesting the url " + url + address + "\n")
        print(e)
    return county

def get_real_county_by_zip(address):
    url = 'http://maps.googleapis.com/maps/api/geocode/json?address='
    try:
        r = requests.get(url+str(address))
        r_json = r.json()
        county = r_json['results'][0]['address_components'][2]['long_name']
        state = r_json['results'][0]['address_components'][3]['short_name']
    except Exception as e:
        print("Error occurred while requesting the url " + url + address + "\n")
        print(e)
    print(county + " ")
    return (county,state)

def get_county(url, zip_code):
    try:
        r = requests.get(url+zip_code)
    except Exception as e:
        print("Error occurred while requesting the url " + url + zip_code + "\n")
        print(e)
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
    db = _mysql.connect("localhost", "iris", "phoebebooboo", "public_county_pages")
    query = """insert into fb_pages (id, page_name, page_url, page_state, page_county) Values('%s', '%s', '%s', '%s', '%s', '%s')""" % (page_id, page_name, page_url, page_state, page_county, search_query)
    db.insert(query)

if __name__ == "__main__":
    main()
