"""
import json, os, time
import pandas as pd
from cs50 import SQL
"""
import spacy
import re
from difflib import SequenceMatcher

NER = spacy.load("model-last")

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
    elif inputStr == 'nt':
        return "number_theory"
    elif len(inputStr) <= 7:
        return List[index] 
    return 0
    

def ratings (string, order):
    normal_list = re.findall('\d+\.\d+', string)
    for i in normal_list: string.replace(i, "")
    normal_list += re.findall('\d+', string)
    normal_list = [round(float(number)) for number in normal_list]
    if order == "RANGE":
        start = min(normal_list)
        end = max(normal_list)
        if start < 2 or end > 4:
            return 0
        else:
            return list(range(start, end+1))
    elif order == "RATING":
        normal_list =  list(set(normal_list))
        if normal_list[0] < 2 or normal_list[len(normal_list)-1] >4:
            return 0
        else:
            return normal_list

def check_topic(txt):
    #since this function will be used by high lvl users such as admins more often
    tags = {'geometry':'g', 'geo':'g', 'g':'g',
            'algebra':'a', 'alge':'a', 'a':'a',
            'number_theory':'n', 'nt':'n', 'n':'n',
            'combinatorics':'c', 'combi':'c', 'c':'c'} #tags
    med = txt.strip().lower()
    return tags[med] if med in tags else 0


def check_source(txt):
    #the format of a problem ID is
    #{abbr}{year in 4 digit after 1959}p{integer}
    #return original string if valid, false otherwise
    return txt.lower()

def check_number_pset(number):
    number = int(number)
    if number >=1 and number <=5:
        return number
    else: return

def NLP(content):
    text = NER(content)
    return [(word.text, word.label_) for word in text.ents]

def text_transform(text):
    for number in numbers:
        text = text.replace(number, f" {numbers[number]} ")
    return text.replace("  ", " ").strip()

"""  
from cs50 import SQL
db = SQL("sqlite:///test.db")
a = db.execute("SELECT id FROM testing")[0]
print(type(a['id']))

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