from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for, session
from langchain_community.document_loaders import PyMuPDFLoader
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import sqlite3
from rag.chatbot import ask_question,analyze_prescription

app = Flask(__name__)
app.secret_key = "medicare123"
app.permanent_session_lifetime = timedelta(days=7)


# ---------------- DATABASE ---------------- #

def create_database():

    conn = sqlite3.connect("medicare.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chats(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        question TEXT,
        answer TEXT,
        conversation_id INTEGER
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patient_profile(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        age TEXT,
        gender TEXT,
        blood_group TEXT,
        allergies TEXT,
        medical_history TEXT
                   
    )
    """)
   
    conn.commit()
    conn.close()

    print("✅ Database Ready")


create_database()


# ---------------- HOME ---------------- #

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- LOGIN ---------------- #

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("medicare.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        user = cursor.fetchone()

        if user:

            if check_password_hash(user[3], password):

                session.permanent = True
                session["user"] = email

                # Create first conversation
                cursor.execute(
                    "INSERT INTO conversations(user_email) VALUES(?)",
                    (email,)
                )

                conn.commit()

                session["conversation_id"] = cursor.lastrowid

                conn.close()

                return redirect(url_for("dashboard"))

            conn.close()

            return render_template(
                "login.html",
                error="Incorrect password."
            )

        conn.close()

        return render_template(
            "login.html",
            error="Account not found. Please register first."
        )

    return render_template("login.html")


# ---------------- DASHBOARD ---------------- #

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("medicare.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM users WHERE email=?",
        (session["user"],)
    )

    user = cursor.fetchone()

    cursor.execute("""
    SELECT question, answer
    FROM chats
    WHERE user_email=? AND conversation_id=?
    ORDER BY id DESC
    """,
    (
        session["user"],
        session["conversation_id"]
    ))

    history = cursor.fetchall()

    cursor.execute("""
    SELECT id
    FROM conversations
    WHERE user_email=?
    ORDER BY id DESC
    """,
    (session["user"],)
    )

    conversations = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        user=user,
        history=history,
        conversations=conversations
    )
# ---------------- ASK AI ---------------- #

@app.route("/ask", methods=["POST"])
def ask():

    if "user" not in session:
        return redirect(url_for("login"))

    question = request.form["question"]
   
  
    conn = sqlite3.connect("medicare.db")
    cursor = conn.cursor()
    cursor.execute(
    "SELECT age, gender, blood_group, allergies, medical_history FROM patient_profile WHERE user_email=?",
    (session["user"],)
)

    profile = cursor.fetchone()
    answer = ask_question(question,profile)



    # Save current conversation message
    cursor.execute(
        """
        INSERT INTO chats(user_email, question, answer, conversation_id)
        VALUES(?,?,?,?)
        """,
        (
            session["user"],
            question,
            answer,
            session["conversation_id"]
        )
    )

    conn.commit()

    # User name
    cursor.execute(
        "SELECT name FROM users WHERE email=?",
        (session["user"],)
    )

    user = cursor.fetchone()

    # Current conversation history
    cursor.execute("""
    SELECT question, answer
    FROM chats
    WHERE user_email=? AND conversation_id=?
    ORDER BY id DESC
    """,
    (
        session["user"],
        session["conversation_id"]
    ))

    history = cursor.fetchall()

    # Sidebar conversations
    cursor.execute("""
    SELECT id
    FROM conversations
    WHERE user_email=?
    ORDER BY id DESC
    """,
    (session["user"],)
    )

    conversations = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        user=user,
        history=history,
        conversations=conversations
    )


# ---------------- REGISTER ---------------- #

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect("medicare.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:

            conn.close()

            return render_template(
                "register.html",
                error="Email already registered."
            )

        cursor.execute(
            "INSERT INTO users(name,email,password) VALUES(?,?,?)",
            (name, email, hashed_password)
        )

        conn.commit()

        session.permanent = True
        session["user"] = email

        # First conversation
        cursor.execute(
            "INSERT INTO conversations(user_email) VALUES(?)",
            (email,)
        )

        conn.commit()

        session["conversation_id"] = cursor.lastrowid

        conn.close()

        return redirect(url_for("dashboard"))

    return render_template("register.html")


# ---------------- NEW CHAT ---------------- #

@app.route("/new_chat", methods=["POST"])
def newchat():

    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("medicare.db")
    cursor = conn.cursor()

    # Create new conversation
    cursor.execute(
        "INSERT INTO conversations(user_email) VALUES(?)",
        (session["user"],)
    )

    conn.commit()

    session["conversation_id"] = cursor.lastrowid

    cursor.execute(
        "SELECT name FROM users WHERE email=?",
        (session["user"],)
    )

    user = cursor.fetchone()

    cursor.execute("""
    SELECT id
    FROM conversations
    WHERE user_email=?
    ORDER BY id DESC
    """,
    (session["user"],)
    )

    conversations = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        user=user,
        history=[],
        conversations=conversations
    )


# ---------------- LOGOUT ---------------- #

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))
# ---------------- PROFILE ---------------- #

@app.route("/profile", methods=["GET","POST"])
def profile():
      if "user" not in session:
        return redirect(url_for("login"))
      if request.method=="POST":
          age = request.form["age"]
          gender = request.form["gender"]
          blood_group = request.form["blood_group"]
          allergies = request.form["allergies"]
          medical_history = request.form["medical_history"]
          conn=sqlite3.connect("medicare.db")
          cursor=conn.cursor()
          cursor.execute(
    "SELECT * FROM patient_profile WHERE user_email=?",
    (session["user"],)
)

          profile = cursor.fetchone()
          if profile:
              cursor.execute("""
UPDATE patient_profile
SET
age=?,
gender=?,
blood_group=?,
allergies=?,
medical_history=?
WHERE user_email=?
""",
(
    age,
    gender,
    blood_group,
    allergies,
    medical_history,
    session["user"]
))
          else:
              cursor.execute(
              
        
              """
INSERT INTO patient_profile
(user_email, age, gender, blood_group, allergies, medical_history)
VALUES (?, ?, ?, ?, ?, ?)
""",
(
    session["user"],
    age,
    gender,
    blood_group,
    allergies,
    medical_history
))
          conn.commit()
          conn.close()
          return redirect(url_for("dashboard"))
      if request.method=="GET":
          
          conn = sqlite3.connect("medicare.db")
          cursor = conn.cursor()

          cursor.execute(
    "SELECT * FROM patient_profile WHERE user_email=?",
    (session["user"],)
)

          profile = cursor.fetchone()

          conn.close()
      return render_template("profile.html", profile=profile)

# UPLOAD PDF PROFILE
@app.route("/upload_prescription", methods=["POST"])
def upload_prescription():
    conn = sqlite3.connect("medicare.db")
    cursor = conn.cursor()
    if "user" not in session:
        return redirect(url_for("login"))
    
    file = request.files["prescription"]
    filename = secure_filename(file.filename)
    filepath = os.path.join("uploads", filename)
    file.save(filepath)
    if file.filename == "":
            return "No file selected"

    loader = PyMuPDFLoader(filepath)

    documents = loader.load()

    text = ""

    for doc in documents:
        text += doc.page_content + "\n"

    text = text[:3000]
    analysis = analyze_prescription(text)
    
    cursor.execute(
    "SELECT name FROM users WHERE email=?",
    (session["user"],)
)

    user = cursor.fetchone()
    cursor.execute("""
SELECT question, answer
FROM chats
WHERE user_email=? AND conversation_id=?
ORDER BY id DESC
""",
(
    session["user"],
    session["conversation_id"]
))

    history = cursor.fetchall()
    cursor.execute("""
SELECT id
FROM conversations
WHERE user_email=?
ORDER BY id DESC
""",
(session["user"],)
)

    conversations = cursor.fetchall()
    conn.close()
    return render_template(
    "dashboard.html",
    user=user,
    history=history,
    conversations=conversations,
    prescription_analysis=analysis
)


    

    
# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)