import sqlite3

## connect to sqlite3

connection = sqlite3.connect("student.db")

## create a cursor to insert record,create table 

cursor = connection.cursor()

## create the table 

table_info ="""

create table STUDENT(NAME VARCHAR(25),CLASS VARCHAR(25),SECTION VARCHAR(25),MARKS INT)
"""

cursor.execute(table_info)

## insert some more records 

cursor.execute('''INSERT INTO STUDENT VALUES('BHUVAN','DATA SCIENCE','A',90)''')
cursor.execute('''INSERT INTO STUDENT VALUES('YASHWANTH','DATA SCIENCE','B',95)''')
cursor.execute('''INSERT INTO STUDENT VALUES('BHUVANESH','COMPUTER SCIENCE','B',92)''')
cursor.execute('''INSERT INTO STUDENT VALUES('UDAY','DATA SCIENCE','C',85)''')

## Display all the records 

print("The inserted records are")

data = cursor.execute('''SELECT * FROM STUDENT''')

## SO obviously rows are in the form of lists here so we should execute a for loop 

for row in data:
    print(row)

## Commit the changes made to the database 

connection.commit()

connection.close()



