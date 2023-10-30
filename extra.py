import json, os, time
import pandas as pd
from cs50 import SQL


def check1(msg, goal):
    #check the message doesnt contain first word as $some_comand
    #check if the message is valid according to goal
    #return the topic as "A" or "C"
    #return the number as integer
    #return the list of tuples(where separated by and)
    #return the list of ratings(int) possible duplicates 
    #return the error code according to error_code.txt
    if msg == "": return "1"
    return 0

"""
db = SQL("sqlite:///test.db")
a = db.execute("SELECT * FROM test WHERE name = ?", 'soe')
print(a)
"""