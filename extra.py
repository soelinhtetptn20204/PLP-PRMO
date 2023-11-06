"""
import json, os, time
import pandas as pd
from cs50 import SQL
"""
import re
from difflib import SequenceMatcher

with open("tags.txt") as f:
    tags = [tag.strip() for tag in f]

numbers = {"one": "1", "two": "2", "three": "3",
           "four": "4", "five": "5", "six":"6",
           "seven": "7", "eight": "8", "nine": "9"}

def check_tag (List=tags, inputStr=""):
    Max = SequenceMatcher(a = List[0], b = inputStr).ratio()
    index = 0
    for i in range(len(List)):
        percent = SequenceMatcher(a = List[i], b = inputStr).ratio()
        if percent > Max:
            Max = percent
            index = i
    if Max > 0.7:
        return List[index]
    elif inputStr == 'fe':
        return "functional_eq"
    elif len(inputStr) <= 7:
        return List[index] 
    else:
        return 0
    

def ratings (string, order):
    for number in numbers:
        if number in string:
            string.replace(number, numbers[number])
    normal_list = re.findall('\d+\.\d+', string)
    for i in normal_list: string.replace(i, "")
    normal_list += re.findall('\d+', string)
    normal_list = [round(float(number)) for number in normal_list]
    if order == "RANGE":
        start = min(normal_list)
        end = max(normal_list)
        if start < 1 or end > 4:
            return 0
        else:
            return list(range(start, end+1))
    elif order == "RATING":
        normal_list =  list(set(normal_list))
        if normal_list[0] < 1 or normal_list[len(normal_list)-1] >4:
            return 0
        else:
            return normal_list


def check_topic(txt):
    #check if topic is valid outta a,c,g,n
    #return A for algebra, C for combi and so on
    #return false otherwise
    return txt


def check_source(txt):
    #the format of a problem ID is
    #{abbr}{year in 4 digit after 1959}p{integer 1 to 30}
    #return original string if valid, false otherwise
    return txt

"""
db = SQL("sqlite:///test.db")


TEMPORARY
@bot.command(name="recommend", help="Just uses $recommend in DM")
@commands.max_concurrency(1,per=commands.BucketType.default,wait=False)
#@commands.cooldown(1, 250, commands.BucketType.default)
async def _recommend(ctx):
    user = ctx.author
    if not member_valid(user):
        await ctx.send("Please rejoin the server to request problems.")
        return
    query = {
        "Topic u'd like to do": "",
        "How many questions": "",
        "Problem-theme Tags": "comma ',' or 'and' for union",
        "Difficulty rating": f"You can refer to problem rating numbers and usage in the <#{RULES}>."
    }
    for q in query:
        for i in range(3):
            await ctx.send(f"{q}? {query[q]}")
            try:
               message = await bot.wait_for("message", timeout=60)
            except:
               await ctx.send("Time out. Please msg me $recommend for problem req")
            if check1(message.content, q) not in {'1','2','3','4','5'}:
                query[q] = message.content
                break
            if i == 2:
               await ctx.send("Try again. Message me $recommend for problem req")
               return
    return
"""