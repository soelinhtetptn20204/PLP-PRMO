import json, os, time
import pandas as pd
from cs50 import SQL


def check_topic(txt):
    #blank so far
    return 0

"""
db = SQL("sqlite:///test.db")
a = db.execute("SELECT * FROM test WHERE name = ?", 'soe')
print(a)

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