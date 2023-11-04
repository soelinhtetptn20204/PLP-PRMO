"""
import json, os, time
import pandas as pd
from cs50 import SQL
"""

def check_source(txt):
    #check if topic is valid outta a,c,g,n
    #return A for algebra, C for combi and so on
    #return false otherwise
    return txt

def check_topic(txt):
    #the format of a problem ID is
    #{abbr}{year in 4 digit after 1959}p{integer 1 to 30}
    #return original string if valid, false otherwise
    return txt

"""
db = SQL("sqlite:///test.db")


"""

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
#"""