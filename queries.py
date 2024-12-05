'''
testing how to query the database through a seperate interface
'''

import psycopg2
from psycopg2 import sql

def main():
    conn = psycopg2.connect(dbname='mtg_db', user='oliver', password='swipeit63', host='localhost')

    # placeholder menu to test functions
    print("Welcome to the MTG card finder. Press any key to continue.")
    input()  # Wait for user input to proceed

    while True:
        query_type = input(
            "\nOptions:\n"
            "1. Search for cards containing specific oracle text.\n"
            "2. Find the oracle text of a given card name.\n"
            "q. End the program.\n"
            "Enter your choice: "
        )

        if query_type == 'q':
            print("Goodbye!")
            break
        elif query_type == '1':
            txt = input("Enter oracle text to find matching cards: ")
            results = search_cards(txt.lower(), 'oracle_text', conn)
            if len(results) == 0:
                print("No results found.")
            else:
                print("\nMatching Cards:")
                for name in results:
                    print(name)
        elif query_type == '2':
            name = input("Enter a card name to find its oracle text: ")
            result = return_card_info(name.lower(), conn)
            if len(result) == 0:
                print("No results found.")
            else:
                mana_cost, type, oracle, image_uri_normal, image_uri_large, image_uri_art_crop = result[0]
                print(f"\n{name}  {mana_cost}")
                print(f"{type}")
                print("\n" + oracle)
                print(f"Image URIs: normal={image_uri_normal}, large={image_uri_large}, art_crop={image_uri_art_crop}")
        else:
            print("Invalid option. Please try again.")

def search_cards(text, col, conn):
    """
    Query the database for cards containing specific oracle text, returning a list of card names.
    Eventually should return 'card objects' containing all info about the found cards.
    """
    query = f"SELECT name FROM cards WHERE LOWER({col}) LIKE LOWER('%{text}%')"

    with conn.cursor() as cursor:
        cursor.execute(query)
        results = [list(row) for row in cursor.fetchall()]
    cursor.close()
    return results

def return_card_info(name, conn):
    """
    Given a card name, return its info including image URIs
    """
    query = """
        SELECT mana_cost, type_line, oracle_text, 
               image_uri_normal, image_uri_large, image_uri_art_crop 
        FROM cards 
        WHERE LOWER(name)=LOWER(%s) 
        LIMIT 1
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (name,))
        result = [list(row) for row in cursor.fetchall()]
        cursor.close()
        return result

if __name__ == '__main__':
    main()