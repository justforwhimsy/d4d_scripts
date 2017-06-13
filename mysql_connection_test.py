import _mysql

db = _mysql.connect("localhost", "user", "password", "public_county_pages")



new_row = """insert into fb_pages (id, page_name, page_url, page_state, page_county) Values("1234552", "Test", "http://test.com", 'ts', 'test county') """
# db.query(new_row)
page_id = "1234553"
page_name ="Test"
page_url = "http://test.com"
page_state = "OR"
page_county = "Multnomah County"
query = """insert into fb_pages (id, page_name, page_url, page_state, page_county) Values('%s', '%s', '%s', '%s', '%s')""" % (page_id, page_name, page_url, page_state, page_county)
db.query(query)
content = db.query("""select * from fb_pages""")

results = db.use_result()

print(results.fetch_row(0))
