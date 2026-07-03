from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "pollsurveysecret"

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS polls(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS votes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        poll_id INTEGER,
        option_selected TEXT
    )
    ''')

    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return redirect('/login')

@app.route('/register', methods=['GET','POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        try:
            c.execute(
                "INSERT INTO users(username,password) VALUES(?,?)",
                (username,password)
            )
            conn.commit()

        except:
            return "User already exists"

        conn.close()

        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username,password)
        )

        user = c.fetchone()

        conn.close()

        if user:
            session['user'] = username
            return redirect('/dashboard')

        return "Invalid Login"

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():

    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    c.execute("SELECT * FROM polls")
    polls = c.fetchall()

    total_polls = len(polls)

    c.execute("SELECT COUNT(*) FROM votes")
    total_votes = c.fetchone()[0]

    
    return render_template(
    'dashboard.html',
    polls=polls,
    total_polls=total_polls,
    total_votes=total_votes
)

@app.route('/create_poll', methods=['GET','POST'])
def create_poll():

    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':

        question = request.form['question']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute(
            "INSERT INTO polls(question) VALUES(?)",
            (question,)
        )

        conn.commit()
        conn.close()

        return redirect('/dashboard')

    return render_template('create_poll.html')


@app.route('/vote/<int:poll_id>', methods=['GET','POST'])
def vote(poll_id):

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute(
        "SELECT * FROM polls WHERE id=?",
        (poll_id,)
    )

    poll = c.fetchone()

    if request.method == 'POST':

        vote = request.form['vote']

        c.execute(
            "INSERT INTO votes(poll_id,option_selected) VALUES(?,?)",
            (poll_id,vote)
        )

        conn.commit()
        conn.close()

        return redirect('/results/' + str(poll_id))

    conn.close()

    return render_template(
        'vote.html',
        poll=poll
    )


@app.route('/results/<int:poll_id>')
def results(poll_id):

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute(
        "SELECT * FROM polls WHERE id=?",
        (poll_id,)
    )

    poll = c.fetchone()

    c.execute(
        "SELECT COUNT(*) FROM votes WHERE poll_id=? AND option_selected='Yes'",
        (poll_id,)
    )

    yes_votes = c.fetchone()[0]

    c.execute(
        "SELECT COUNT(*) FROM votes WHERE poll_id=? AND option_selected='No'",
        (poll_id,)
    )

    no_votes = c.fetchone()[0]

    conn.close()

    return render_template(
        'results.html',
        poll=poll,
        yes=yes_votes,
        no=no_votes
    )


@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect('/login')

@app.route('/delete_poll/<int:poll_id>')
def delete_poll(poll_id):

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute(
        "DELETE FROM votes WHERE poll_id=?",
        (poll_id,)
    )

    c.execute(
        "DELETE FROM polls WHERE id=?",
        (poll_id,)
    )

    conn.commit()
    conn.close()

    return redirect('/dashboard')


if __name__ == '__main__':
    app.run(debug=True)