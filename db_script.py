import os
import psycopg2
from psycopg2 import sql
import json
import requests

def create_table(conn):
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cards (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                mana_cost VARCHAR(15),
                cmc VARCHAR(15)
                type_line VARCHAR(100),
                rarity VARCHAR(20),
                set_name VARCHAR(100)
                set_id INT REFERENCES sets(set_id)
            )
        """)
        conn.commit()

def create_set_table(conn):
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE sets (
                set_id SERIAL PRIMARY KEY,
                code VARCHAR(10)
                set_name VARCHAR(100)
                set_type VARCHAR(25)
                block VARCHAR(50)
            )
        """)

# Function to fetch card data from Scryfall
def fetch_card_data():
    # Get the current script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Specify the JSON file name
    json_file_path = os.path.join(script_dir, 'all_cards.json')  # Replace with your actual file name

    # Open and load the JSON file
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    return data

# Function to insert card data into the database
def insert_card_data(conn, card):
    with conn.cursor() as cursor:
        insert_query = sql.SQL("""
            INSERT INTO cards (name, mana_cost, type_line, rarity, set_name, )
            VALUES (%s, %s, %s, %s, %s)
        """)
        cursor.execute(insert_query, (
            card.get('name'),
            card.get('mana_cost'),
            card.get('type_line'),
            card.get('rarity'),
            card.get('set_name')
        ))
    conn.commit()

def insert_set_data(conn, set):
    pass
        

def main():
    # connect to database
    conn = psycopg2.connect(dbname='mtg_db', user='oliver', password='swipeit63', host='localhost')

    if conn:
        # fetch set data
        url = 'https://api.scryfall.com/sets'
        response = requests.get(url)

        if response.status_code == 200:
            sets_data = response.json()

            for set in sets_data:
                insert_set_data(conn, set)
        else:
            print(f"Error: {response.status_code}")

        create_table(conn)
        # fetch card data
        card_data = fetch_card_data()
        for card in card_data:
            insert_card_data(conn, card)

        conn.close()
        print("Data inserted successfully!")

if __name__ == '__main__':
    main()
