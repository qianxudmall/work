#!/usr/bin/python
# -*- coding:utf-8 -*-
import MySQLdb
import mysql_conf
import logging

# get mysql connection
def get_connection():
    try:
        conn = MySQLdb.connect(host=mysql_conf.DB_HOST, user=mysql_conf.USER,
                                passwd=mysql_conf.PASSWORD, db=mysql_conf.DATABASE, charset="utf8")
        return conn
    except Exception as e:
        logging.warn(e)

# close connection and cursor
def close(conn, cursor):
    if cursor:
       try:
           cursor.close()
       except Exception as e:
           logging.warn(e)
    if conn:
        try:
            conn.close()
        except Exception as e:
            logging.warn(e)

if __name__ == '__main__':
    conn = get_connection()
    print(conn)
    close(conn,None)
