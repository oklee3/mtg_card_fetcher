from flask import Flask, jsonify, request, render_template
import psycopg2
from psycopg2.extras import RealDictCursor
from functools import wraps
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

def get_db_connection():
    """Database connection factory"""
    return psycopg2.connect(
        dbname='mtg_db',
        user='oliver',
        password='swipeit63',
        host='localhost'
    )

def db_handler(f):
    """Decorator to handle database connections"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        conn = get_db_connection()
        try:
            result = f(conn, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            return jsonify({'error': str(e)}), 500
        finally:
            conn.close()
    return wrapper

@app.route('/api/cards', methods=['GET'])
@db_handler
def get_cards(conn):
    """Get all cards with optional filtering"""
    name = request.args.get('name')
    
    query = "SELECT * FROM cards WHERE 1=1"
    params = []
    
    if name:
        query += " AND LOWER(name) LIKE LOWER(%s)"
        params.append(f'%{name}%')
    
    query += " LIMIT 100"  # Prevent overwhelming responses
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, params)
        cards = cur.fetchall()
    return jsonify(cards)

@app.route('/api/cards/<card_name>', methods=['GET'])
@db_handler
def get_card_by_name(conn, card_name):
    """Get specific card by name"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM cards WHERE LOWER(name) = LOWER(%s)", (card_name,))
        card = cur.fetchone()
        if card is None:
            return jsonify({'error': 'Card not found'}), 404
    return jsonify(card)

if __name__ == '__main__':
    app.run(debug=True)
