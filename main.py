from replit import db
from flask import Flask, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import sqlite3
import os
import json

# Make an upvote system later.

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_word(word_id):
    conn = get_db_connection()
    word = conn.execute('SELECT * FROM defs WHERE id = ?',
                        (word_id, )).fetchone()
    conn.close()
    if word == None:
        abort(404)
    return word

def get_author(name):
    conn = get_db_connection()
    author = conn.execute('SELECT * FROM authors WHERE name = ?',
                         (name, )).fetchone()
    conn.close()
    if author == None:
        abort(404)
    return author


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["secret"]
admin = ["JBloves27"]
# db["number_of_posts"] = 3
# print(db.keys())
# db["number_of_users"] = 1

@app.route('/')
def index():
  conn = get_db_connection()
  words = conn.execute('SELECT * FROM defs').fetchall()
  conn.close()
  return render_template(
    "index.html",
    user_id = request.headers["X-Replit-User-Id"],
    username = request.headers["X-Replit-User-Name"],
    words = list(reversed(words)) # automatically set to newest first - add a switch preset later with settings
  )

@app.route('/login')
def login():
  user_id = request.headers["X-Replit-User-Id"]
  username = request.headers["X-Replit-User-Name"]
  if user_id:
    conn = get_db_connection()
    conn.execute("INSERT INTO authors (name, words_created) VALUES (?, ?)",
                         (username,0))
    conn.commit()
    conn.close()
    db["number_of_users"] += 1
    return redirect(url_for('index'))
  else:
    return render_template(
      "login.html",
      user_id = user_id,
      username = username
    )

@app.route('/author/<name>')
def author(name):
  the_author = get_author(name)
  if name in admin:
    is_admin = True;
  else: 
    is_admin = False;
  return render_template(
    "author.html",
    user_id = request.headers["X-Replit-User-Id"],
    username = name,
    words_created = the_author["words_created"],
    author = the_author,
    is_admin = is_admin
  )

@app.route('/word/<int:word_id>')
def word(word_id):
  the_word = get_word(word_id)
  if len(the_word["word"]) > 10:
    word = the_word["word"]
    word = word[:11]
    word += "..."
  else:
    word = the_word["word"]
  return render_template(
    "word.html",
    user_id = request.headers["X-Replit-User-Id"],
    username = request.headers["X-Replit-User-Name"],
    word = word,
    content = the_word["content"],
    author = the_word["author"],
    created = the_word["created"],
    id = the_word["id"]
  )

@app.route('/edit/<int:id>', methods = ["GET", "POST"])
def edit(id):
  the_word = get_word(id)
  if request.method == "POST":
    word = request.form["word"]
    definition = request.form["definition"]

    if len(word.split()) > 1:
      flash("Word must be one word! (duh ;-;)")
    elif not word:
      flash("Word name is required!")
    elif not definition:
      flash("Definition is required!")
    else:
      conn = get_db_connection()
      conn.execute(
        'UPDATE defs SET word = ?, content = ?'
        ' WHERE id = ?', (word, definition, id)
      )
      conn.commit()
      conn.close()
      try:
        return redirect(url_for('word', word_id = id))
      except:
        return redirect(url_for('index'))
  return render_template(
    "edit.html",
    word = the_word,
    user_id = request.headers["X-Replit-User-Id"],
    username = request.headers["X-Replit-User-Name"]
  )

@app.route('/create', methods = ["GET", "POST"])
def create():
  if request.method == "POST":
    word = request.form["word"]
    definition = request.form["definition"]
    author = request.headers["X-Replit-User-Name"]
    
    blacklist = open("blacklist.txt")
    blacklist = blacklist.read().lower().splitlines()

    if author.lower() in blacklist:
      flash("You have been banned from posting!")
    elif len(word.split()) > 1:
      flash("Word must be one word! (duh ;-;)")
    elif not word:
      flash("Word name is required!")
    elif not definition:
      flash("Definition is required!")
    else:
      conn = get_db_connection()
      conn.execute("INSERT INTO defs (word, content, author) VALUES (?, ?, ?)",
                         (word,definition,author))
      conn.commit()
      conn.close()
      db["number_of_posts"] += 1
      
      the_author = get_author(author)
      words_created = the_author["words_created"]
      words_created+=1
      number_of_users = db["number_of_users"]
      conn = get_db_connection()
      conn.execute(
        'UPDATE authors SET words_created = ?'
        ' WHERE id = ?', (words_created, number_of_users)
      )
      conn.commit()
      conn.close()
      return redirect(url_for('word', word_id = db["number_of_posts"]))
  return render_template(
    "create.html",
    user_id = request.headers["X-Replit-User-Id"],
    username = request.headers["X-Replit-User-Name"]
  )

@app.route('/delete/<int:id>')
def delete(id):
  word = get_word(id)
  conn = get_db_connection()
  conn.execute("DELETE from defs where id = ?", (id, ))
  conn.commit()
  conn.close()
  flash('"{}" was successfully deleted!'.format(word['word']))
  return redirect(url_for('index'))
  
@app.errorhandler(404)
def not_found(e):
  return render_template(
    "404.html",
    error=e,
    user_id = request.headers["X-Replit-User-Id"],
    username = request.headers["X-Replit-User-Name"]
  )

if __name__ == "__main__":
  app.run(host = "0.0.0.0", port = 8080)