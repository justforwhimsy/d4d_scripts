import requests

def main():
	url = 'http://maps.googleapis.com/maps/api/geocode/json?address='
	zip_code = 97211
	# get filename
	response = get_county(url, str(zip_code))
	r_json = response.json()
	county = r_json['results'][0]['address_components'][2]['long_name']
	state = r_json['results'][0]['address_components'][3]['short_name']
	print(county)
	print(state)

def get_county(url, zip_code):
    try:
        r = requests.get(url+zip_code)
    except Exception as e:
        print("Error occurred while requesting the url " + url + zip_code + "\n")
        print(e)
    return r

if __name__ == "__main__":
    main()