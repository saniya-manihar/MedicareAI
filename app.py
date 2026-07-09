from flask import Flask, render_template,request,redirect,url_for,session
import sqlite3
from rag.chatbot import ask_question
app=Flask(__name__)
app.secret_key = "medicare123"


def create_database():

    conn = sqlite3.connect("medicare.db")

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        password TEXT
    )
    """)

    conn.commit()

    conn.close()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        conn = sqlite3.connect("medicare.db")
        cursor = conn.cursor()

        email = request.form["email"]
        password = request.form["password"]

        print("Email:", email)
        print("Password:", password)

        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        user = cursor.fetchone()

        conn.close()

        if user:

            print("User Found")

            if password == user[3]:

                print("Password Match")

                session["user"] = email

                return redirect(url_for("dashboard"))

            else:

                return render_template(
                    "login.html",
                    error="Incorrect password."
                )

        else:

            return render_template(
                "login.html",
                error="Account not found. Please register first."
            )

    return render_template("login.html")     
          
          
@app.route("/dashboard")
def dashboard():

    if "user" in session:
        return render_template("dashboard.html")

    return redirect(url_for("login"))
@app.route("/ask", methods=["POST"])
def ask():

    if "user" not in session:
        return redirect(url_for("login"))

    question = request.form["question"]

    answer = ask_question(question)

    return render_template(
        "dashboard.html",
        answer=answer,
        question=question
    )

             
            
@app.route("/logout")
def logout():
     session.pop("user", None)
     return redirect(url_for("login"))
   
         
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        conn = sqlite3.connect("medicare.db")
        cursor = conn.cursor()

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        cursor.execute(
            "INSERT INTO users(name,email,password) VALUES(?,?,?)",
            (name, email, password)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")
       

if __name__ == "__main__":
    create_database()
    app.run(debug=True)




