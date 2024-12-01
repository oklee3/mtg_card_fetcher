'''
oliver lee

create database tables, updates with current sets each time it is run
'''

import os
import psycopg2
from psycopg2 import sql
import json
import requests

def create_cards_table(conn):
    """
    Creates the table of all cards from a stored json file.
    """
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cards (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                mana_cost VARCHAR(255),
                cmc VARCHAR(255),
                type_line VARCHAR(255),
                oracle_text TEXT,
                rarity VARCHAR(100),
                set_name VARCHAR(255),
                set_id INT REFERENCES sets(set_id)
            )
        """)
        conn.commit()

def create_set_table(conn):
    """
    Creates the table of all sets from Scryfall API.
    """
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sets (
                set_id SERIAL PRIMARY KEY,
                code VARCHAR(10),
                set_name VARCHAR(255),
                set_type VARCHAR(255),
                block VARCHAR(255)
            )
        """)

def fetch_card_data():
    """
    Fetches a json file of all cards i have stored somewhere else (its too big).
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(script_dir, '/Users/oliver/Documents/big_files/all_cards.json')

    with open(json_file_path, 'r') as file:
        data = json.load(file)
    return data

def insert_card_data(conn, card):
    """
    Populates each column of the cards table.
    """
    with conn.cursor() as cursor:
        insert_query = sql.SQL("""
            INSERT INTO cards (name, mana_cost, cmc, type_line, oracle_text, rarity, set_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """)
        cursor.execute(insert_query, (
            card.get('name'),
            card.get('mana_cost'),
            card.get('cmc'),
            card.get('type_line'),
            card.get('oracle_text'),
            card.get('rarity'),
            card.get('set_name')
        ))
    conn.commit()

def insert_set_data(conn, set):
    """
    Populates the sets table.
    """
    with conn.cursor() as cursor:
        insert_query = sql.SQL("""
            INSERT INTO sets (code, set_name, set_type, block)
            VALUES (%s, %s, %s, %s)
        """)
        cursor.execute(insert_query, (
            set.get('code'),
            set.get('name'),
            set.get('set_type'),
            set.get('block')
        ))
        

def main():
    # connect to database
    conn = psycopg2.connect(dbname='mtg_db', user='oliver', password='swipeit63', host='localhost')

    if conn:
        create_set_table(conn)
        # fetch set data
        url = 'https://api.scryfall.com/sets'
        response = requests.get(url)

        if response.status_code == 200:
            sets_data = response.json()

            for set in sets_data['data']:
                insert_set_data(conn, set)
        else:
            print(f"Error: {response.status_code}")

        create_cards_table(conn)
        # fetch card data
        card_data = fetch_card_data()
        for card in card_data:
            insert_card_data(conn, card)

        conn.close()
        print("Data inserted successfully!")

if __name__ == '__main__':
    main()
