import requests
from bs4 import BeautifulSoup
import psycopg2

def clean_text(text):
    try:
        # Remove non-UTF-8 characters
        return ''.join(char for char in text if ord(char) < 128)
    except Exception as e:
        print(f"Text cleaning error: {e}")
        return text

def resp(url):
    try:
        # Use requests with additional headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Make the request with custom headers
        response = requests.get(url, headers=headers)
        
        # Try multiple encoding approaches
        response.encoding = response.apparent_encoding or 'utf-8'

        if response.status_code == 200:
            # Use html.parser instead of lxml to avoid parser issues
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the table and extract data
            table = soup.find('div', class_='leaderboard')
            if not table:
                print("Leaderboard table not found on the page.")
                return
            
            elems = table.find_all('tr')

            positions = []
            names = []
            clans = []
            honors = []

            for elem in elems[1:]:
                try:
                    td1 = elem.find_all('td')

                    # Safely extract and clean each piece of data
                    position = clean_text(elem.find('td', class_='rank').text.strip())
                    name = clean_text(elem.find('a').text.strip())
                    
                    # Handle clan with additional safety
                    clan = clean_text(td1[2].text.strip()) if len(td1) > 2 and td1[2].text.strip() else '-'
                    
                    honor = clean_text(td1[3].text.strip())

                    positions.append(position)
                    names.append(name)
                    clans.append(clan)
                    honors.append(honor)

                except Exception as row_error:
                    print(f"Error processing row: {row_error}")
                    continue

                # Print collected data for verification
            print("Collected data:")
            print("Positions:", positions)
            print("Names:", names)
            print("Clans:", clans)
            print("Honors:", honors)

            # Database connection configuration
            db_config = {
                'dbname': 'postgres',
                'user': 'postgres',
                'password': 'Qazxswedc24.',
                'host': 'localhost',
                'port': '5432'
            }   

            connection = None
            cursor = None
            try:
                connection = psycopg2.connect(**db_config)
                cursor = connection.cursor()

                # Create table with more robust column types
                create_table_query = """
                CREATE TABLE IF NOT EXISTS codewars_leaderboard (
                    position TEXT,
                    name TEXT,
                    clan TEXT,
                    honor TEXT
                )
                """
                cursor.execute(create_table_query)
                print("Table created or already exists.")

                # Clear existing data before inserting new data
                cursor.execute("DELETE FROM codewars_leaderboard")

                # Insert data into table
                data = list(zip(positions, names, clans, honors))
                insert_query = """
                INSERT INTO codewars_leaderboard (position, name, clan, honor)
                VALUES (%s, %s, %s, %s)
                """
                cursor.executemany(insert_query, data)
                connection.commit()
                print(f"Successfully inserted {len(data)} rows into the table!")

                
            
            except Exception as db_error:
                print(f"Database error: {db_error}")
                if connection:
                    connection.rollback()

            finally:
                # Close connection
                if cursor:
                    cursor.close()
                if connection:
                    connection.close()

        else:
            print(f"Request error: status code {response.status_code}")

    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    url = 'https://www.codewars.com/users/leaderboard'
    resp(url)

if __name__== '__main__':
    main()
