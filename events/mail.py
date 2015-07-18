#!/usr/bin/python

DB_HOST = '127.0.0.1'
DB_PORT = 3306
DB_NAME = 'tulius'
DB_USER = 'root'
DB_PASS = '123'

import sys
import os
import time
import MySQLdb
from email.utils import parseaddr

headers = []
body = []
is_header = True

for v in sys.stdin.readlines():
    if not is_header:
        body += [v]
    elif (v == '\n'):
        is_header = False
    else:
        headers += [v]
sender, sender_mail = parseaddr(sys.argv[1])
recipient, recipient_mail = parseaddr(sys.argv[2])
headers = ''.join(headers)
body = ''.join(body)
args_list = [sender, sender_mail, recipient, recipient_mail, headers, body]
args_list = [MySQLdb.escape_string(arg) for arg in args_list]

connection = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASS, db=DB_NAME, port=DB_PORT)
try:
    cursor = connection.cursor()
    sql = "INSERT INTO events_incomemail (sender, sender_mail, recipient, recipient_mail, headers, body) " +\
        "VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.execute(sql, args_list)
    connection.commit()
finally:
    connection.close()