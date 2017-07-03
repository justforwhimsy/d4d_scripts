LOAD DATA local INFILE 'C:/Users/Iris/Documents/d4d/counties/zip_code_revised.csv' 
INTO TABLE addresses 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

