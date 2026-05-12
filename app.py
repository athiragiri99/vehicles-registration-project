from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create table
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner TEXT NOT NULL,
            plate TEXT NOT NULL,
            expiry TEXT NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = get_db_connection()
    vehicles = conn.execute('SELECT * FROM vehicles').fetchall()

    total = len(vehicles)
    active = len([v for v in vehicles if v['status'] == 'Active'])
    expired = len([v for v in vehicles if v['status'] == 'Expired'])
    pending = len([v for v in vehicles if v['status'] == 'Pending'])

    conn.close()

    return render_template('index.html',
                           vehicles=vehicles,
                           total=total,
                           active=active,
                           expired=expired,
                           pending=pending)


@app.route('/add', methods=('GET', 'POST'))
def add():
    if request.method == 'POST':
        owner = request.form['owner']
        plate = request.form['plate']
        expiry = request.form['expiry']
        status = request.form['status']

        #convert to date format
        raw_expiry = request.form['expiry']
        expiry = datetime.strptime(raw_expiry, '%Y-%m-%d').strftime('%m/%d/%Y')

        conn = get_db_connection()
        conn.execute('INSERT INTO vehicles (owner, plate, expiry, status) VALUES (?, ?, ?, ?)',
                     (owner, plate, expiry, status))
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('add.html')


@app.route('/search', methods=('GET', 'POST')) 
def search(): 
    results = [] 
    if request.method == 'POST': 
        query = request.form['query'] 
        conn = get_db_connection() 
        results = conn.execute( "SELECT * FROM vehicles WHERE owner LIKE ? OR plate LIKE ?", ('%' + query + '%', '%' + query + '%') ).fetchall() 
        conn.close() 
    return render_template('search.html',results=results)

@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit(id):
    conn = get_db_connection()
    vehicle = conn.execute('SELECT * FROM vehicles WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        owner = request.form['owner']
        plate = request.form['plate']

        # Convert date format
        raw_expiry = request.form['expiry']
        expiry = datetime.strptime(raw_expiry, '%Y-%m-%d').strftime('%m/%d/%Y')

        status = request.form['status']

        conn.execute('''
            UPDATE vehicles
            SET owner = ?, plate = ?, expiry = ?, status = ?
            WHERE id = ?
        ''', (owner, plate, expiry, status, id))

        conn.commit()
        conn.close()
        return redirect('/')

    conn.close()
    return render_template('edit.html', vehicle=vehicle)


@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM vehicles WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)