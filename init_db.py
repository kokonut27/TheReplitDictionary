import sqlite3 

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
  connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO defs (author, word, content) VALUES (?, ?, ?)",
('JBloves27','Replit','An amazing, free, and extensive website for any coder! (Am I wrong tho :D?)'))
cur.execute("INSERT INTO defs (author, word, content) VALUES (?, ?, ?)",
('JBloves27','test','asdfasfegsreg'))
cur.execute("INSERT INTO defs (author, word, content) VALUES (?, ?, ?)",
('JBloves27','test23','asdfasfegsreg'))

connection.commit()
connection.close()