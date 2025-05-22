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
        password=os.environ.get('DB_PASSWORD'),
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
    oracle = request.args.get('oracle')
    cmc = request.args.get('cmc')
    colors = request.args.get('colors')
    colorLogic = request.args.get('colorLogic')
    
    # add params to query to filter for desired cards
    query = "SELECT * FROM cards WHERE 1=1"
    params = []
    
    if name:
        query += " AND LOWER(name) LIKE LOWER(%s)"
        params.append(f'%{name}%')
        
    if oracle:
        # if the card has multiple faces, check all faces for the oracle text
        query += " AND (LOWER(oracle_text) LIKE LOWER(%s) OR LOWER(COALESCE(face_oracle_text, '')) LIKE LOWER(%s) OR LOWER(COALESCE(card_faces->1->>'oracle_text', '')) LIKE LOWER(%s))"
        params.extend([f'%{oracle}%', f'%{oracle}%', f'%{oracle}%'])
    
    if cmc:
        query += " AND CAST(cmc AS NUMERIC) = %s"
        params.append(cmc)

    if colors:
        color_identity = colors.split(",")
        if colorLogic == "all":
            query += " AND color_identity @> %s"
        elif colorLogic == "exact":
            query += """
                AND (SELECT array_agg(x ORDER BY x) FROM unnest(color_identity) x)
                = (SELECT array_agg(x ORDER BY x) FROM unnest(%s) x)
            """
        else:
            if 'C' in color_identity:
                query += " AND color_identity && %s OR color_identity = '{}')"
            else:
                query += " AND color_identity && %s"
        params.append(color_identity)

    query += " ORDER BY name ASC LIMIT 100;"
    print(query)
    print(params)
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, params)
        cards = cur.fetchall()
    return jsonify(cards)

if __name__ == '__main__':
    app.run(debug=True)
