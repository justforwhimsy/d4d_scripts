import wikipedia as wp
import csv

counties = wp.page("Index of U.S. counties")
county_dicts = {}
with open('us_counties_wiki.csv', 'w') as csvfile:
	writer = csv.writer(csvfile, delimiter=',')
	failures = 0
	for county_state in counties.links:
		# print(county_state)
		try:
			county, state = county_state.split(',')
			# writer.writerow([county, state])
			print("County: "+ county + " State " +state)
			if state in county_dicts:
				county_dicts[state].append(county)
			else:
				county_dicts[state] = [county]
		except:
			# print("Error splitting " + county_state)
			failures += 1

	# print('Number of links: ' + str(len(counties.links)))
	# print('Number of failures: ' + str(failures))
for key, value in county_dicts.items():
	print(key + " has " + str(len(value)) + " counties")
