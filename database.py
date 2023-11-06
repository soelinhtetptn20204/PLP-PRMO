from cs50 import SQL

### DATA BASE ***
### DELETE rows from CHILD TABLE if DELETE rows from PARENT TABLE
db = SQL("sqlite:///test.db")

db.execute("CREATE TABLE IF NOT EXISTS members (memberID TEXT PRIMARY KEY,\
             level TEXT, m_rating TEXT, activated INTEGER)")

db.execute("CREATE TABLE IF NOT EXISTS problems (problemID TEXT PRIMARY KEY, problem_statement TEXT UNIQUE NOT NULL,\
            topic TEXT NOT NULL, p_rating REAL)")

db.execute("CREATE TABLE IF NOT EXISTS psets (psetID INTEGER PRIMARY KEY AUTOINCREMENT, topic TEXT, memberID TEXT,\
            p1 TEXT, p2 TEXT, p3 TEXT, p4 TEXT, p5 TEXT)") 

db.execute("CREATE TABLE IF NOT EXISTS tags (tagID INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, topic TEXT NOT NULL)")

db.execute("CREATE TABLE IF NOT EXISTS hints (problemID TEXT PRIMARY KEY, hint_1 TEXT, hint_2 TEXT, hint_3 TEXT,\
           CONSTRAINT constraint_hint FOREIGN KEY (problemID) REFERENCES problems(problemID) ON DELETE CASCADE)")

db.execute("CREATE TABLE IF NOT EXISTS approved (memberID TEXT PRIMARY KEY, number INTEGER)")

#each problem, user and tags
db.execute("CREATE TABLE IF NOT EXISTS each_problem (solving TEXT PRIMARY KEY, hints_used INTEGER, success INTEGER, checked_by TEXT)")
#format {topic}{id}

db.execute("CREATE TABLE IF NOT EXISTS each_user (psetID INTEGER PRIMARY KEY, topic TEXT, req_time TEXT NOT NULL, sub_time TEXT)") 
#format a{userID}

db.execute("CREATE TABLE IF NOT EXISTS each_tag (problemID TEXT PRIMARY KEY, p_rating REAL,\
           CONSTRAINT constraint_tag FOREIGN KEY (problemID) REFERENCES problems(problemID) ON DELETE CASCADE)") 
#format {topic}{tagID}

#users' query
db.execute("CREATE TABLE IF NOT EXISTS queries (prompt TEXT)")
### DATA BASE ***