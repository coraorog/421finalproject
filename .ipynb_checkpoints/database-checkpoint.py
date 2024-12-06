from flask import Flask, g, request, jsonify, render_template, redirect, url_for
import sqlite3
import os

# Initialize the Flask application
app = Flask(__name__)

# Path to the SQLite database file
DATABASE = os.path.join(os.path.dirname(__file__), "Plant_Parenthood.db")

# Helper function to get a database connection
def get_db():
    """
    Get a database connection for the current request context.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE, check_same_thread=False)
        g.db.row_factory = sqlite3.Row  # Optional: Makes rows behave like dictionaries
    return g.db

# Cleanup function to close the database connection after each request
@app.teardown_appcontext
def close_db(exception):
    """
    Close the database connection at the end of the request.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Route: Home page showing available tables
@app.route('/')
def home():
    """
    Display all tables in the database.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cursor.fetchall()]
    return render_template('index.html', tables=tables)

# Route: View records in a specific table with Add/Delete buttons
@app.route('/view/<table_name>')
def view_table(table_name):
    """
    Display all records from a selected table.
    """
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        # Get column names for the table
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]

        return render_template('view.html', table_name=table_name, records=rows, columns=columns)
    except sqlite3.OperationalError as e:
        return jsonify({"error": f"Could not access table '{table_name}': {str(e)}"}), 400

# Route: Add a new record (form view and processing)
@app.route('/add/<table_name>', methods=['GET', 'POST'])
def add_record(table_name):
    """
    Add a new record to the specified table via a web form.
    """
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        # Get form data
        data = {key: value for key, value in request.form.items()}

        if table_name == 'orders':
            # Quality check logic for 'order' table entries
            order_id = data.get('oid') 
            if not order_id:
                return "Error: Missing 'Order ID' field in the form data.", 400
            
            # Fetch the quantity of the specified plant
            cursor.execute("SELECT quantity FROM plants WHERE pid = ?", (order_id,))
            plant_row = cursor.fetchone()
            
            if not plant_row:
                return f"Error: Plant with ID {order_id} does not exist.", 404
            
            plant_quantity = plant_row[2]
            
            # Check if the plant meets the quality criteria
            if plant_quantity <= 0:
                return f"Error: (Plant is out of stock).", 400
            

        # Prepare INSERT query
        placeholders = ", ".join(["?"] * len(data))
        columns = ", ".join(data.keys())
        values = list(data.values())
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(query, values)
        db.commit()
        return redirect(url_for('view_table', table_name=table_name))

    # For GET: Fetch table column names to generate the form
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]
    return render_template('add.html', table_name=table_name, columns=columns)

# Route: Delete a record
@app.route('/delete/<table_name>/<column>/<value>', methods=['POST'])
def delete_record(table_name, column, value):
    """
    Delete a record from the specified table.
    """
    db = get_db()
    cursor = db.cursor()

    # Execute DELETE query
    query = f"DELETE FROM {table_name} WHERE {column} = ?"
    cursor.execute(query, (value,))
    db.commit()
    return redirect(url_for('view_table', table_name=table_name))

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
