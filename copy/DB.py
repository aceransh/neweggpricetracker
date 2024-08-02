from datetime import datetime
import sqlite3

def create_connection():
    try:
        conn = sqlite3.connect('price_tracker.db')
        print("Connection to SQLite DB successful")
        return conn
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred")
        return None


# Create a table to store product information and price history
def create_table(conn):
    try:
        sql_create_product_table = """
        CREATE TABLE IF NOT EXISTS product_database (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            price REAL,
            timestamp TEXT
        );
        """
        conn.execute(sql_create_product_table)
        print("Table creation successful")
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred during table creation")


# insert product data
def insert_product_data(conn, product_data):
    with conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO product_database (name, url, price, shipped_by, sold_by, rating, timestamp) 
            VALUES(:name, :url, :price, :shipped_by, :sold_by, :rating, :timestamp)""",
            {
                'name': product_data.name,
                'url': product_data.url,
                'price': product_data.price,
                'shipped_by': product_data.shipped_by,
                'sold_by': product_data.sold_by,
                'rating': product_data.rating,
                'timestamp': product_data.timestamp
            }
        )
        return cursor.lastrowid
        
# Delete product data from the table based on the product id.
def delete_product_data(conn, product_id):
    with conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM product_database WHERE id = :id", {'id': product_id})

def clear_table(conn):
    with conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM product_database")

def insert_test_data():
    conn = create_connection()
    cursor = conn.cursor()
    
    # Create the table if it doesn't exist
    create_table(conn)
    
    # Insert test data
    cursor.execute("""
    INSERT INTO product_database (name, url, price, shipped_by, sold_by, rating, timestamp) 
    VALUES (?, ?, ?, ?, ?, ?, ?)""", 
    ('ASUS TUF Gaming 23.8" 1080P Monitor (VG249Q1R) - Full HD, IPS, 165Hz (Supports 144Hz), 1ms, Extreme Low Motion Blur, Speaker, FreeSync Premium, Shadow Boost, VESA Mountable, DisplayPort, HDMI', 
     'https://www.newegg.com/black-asus-tuf-gaming-vg249q1r-24/p/N82E16824281256?Item=N82E16824281256', 
     150.00, 
    'Shipped By Test', 'Sold By Test', '4.5', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    conn.commit()
    conn.close()