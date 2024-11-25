import mysql.connector

connection = mysql.connector.connect(
    host="localhost",   # Change to your server's IP if remote
    user="root",
    password="password",
    database="shellforgeDB"
)
cursor = connection.cursor()