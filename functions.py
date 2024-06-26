from database import create_connection, create_table, insert_product_data, delete_product_data, clear_table
from scraper import ProductScraper
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import requests
import os
import re
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# loading env variables
load_dotenv()

EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')
TO_EMAIL = os.getenv('TO_EMAIL')

def connect_sql_to_pandas(conn):
    """
    Fetch data from the SQL database into a pandas DataFrame.
    """
    df = pd.read_sql_query("SELECT * FROM product_database", conn)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def fetch_all_products(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, url, price, timestamp FROM product_database")
    return cursor.fetchall()

def fetch_all_unique_products(conn):
    """
    Fetch all distinct products from the database.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, url, price FROM product_database")
    return cursor.fetchall()

def plot_price_history(conn, product_name):
    df = connect_sql_to_pandas(conn)
    if df.empty:
        print('DataFrame is empty')
        return None

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    product_data = df[df['name'] == product_name]

    plt.figure(figsize=(10, 5))
    plt.plot(product_data['timestamp'], product_data['price'], marker='o', label=product_name[:51])
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.title(f'Price History of {product_name[:51]}')
    plt.legend()

    # Ensure the directory exists
    directory = 'app/static/plots'
    if not os.path.exists(directory):
        os.makedirs(directory)

    sanitized_name = sanitize_filename(product_name[:51])
    image_path = f'{directory}/{sanitized_name}.png'
    plt.savefig(image_path)
    plt.close()

    return image_path

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def display_available_products(conn):
    """
    Display all available products from the database.
    """
    products = fetch_all_products(conn)
    
    product_names = {}
    displayed_names = set()
    for product in products:
        product_id = product[0]
        product_name = product[1]
        if product_name not in displayed_names:
            product_names[product_id] = product_name
            displayed_names.add(product_name)

    print("Available products:")
    for product_id, product_name in product_names.items():
        print(f"{product_id}: {product_name}")
    return product_names

def display_available_products_df(conn):
    """
    Display all available products from the database using pandas DataFrame.
    """
    df = connect_sql_to_pandas(conn)
    unique_products = df.drop_duplicates(subset=['name'])
    product_names = {}
    for index, row in unique_products.iterrows():
        product_id = row['id']
        product_name = row['name']
        product_names[product_id] = product_name
    
    print("Available products:")
    for product_id, product_name in product_names.items():
        print(f"{product_id}: {product_name}")
    return product_names

def automation():
    # Establish a database connection
    conn = create_connection()
    print("Database connection established.")
    
    try:
        # Fetch unique products from the database
        products = fetch_all_unique_products(conn)
        print(f"Fetched {len(products)} unique products from the database.")
        
        # Iterate through each product to scrape the latest price data
        for name, url in products:
            try:
                latest_price = fetch_latest_price(conn, name)
                scraper = ProductScraper(url)
                scraper.fetch_product_data()
                print(f"Scraped data for product: {name}")
                
                # Insert product data into the database and get the assigned ID
                inserted_id = insert_product_data(conn, scraper)
                scraper.id = inserted_id  # Set the ID attribute of the scraper object
                print(f"Inserted data for product: {name} with ID: {inserted_id}")

                # Send email if the latest price is lower
                if latest_price is None or scraper.price < latest_price:
                    subject = f"Price Dropped for {name}"
                    body = f"Old price was ${latest_price if latest_price else 'N/A'} and new price is ${scraper.price}. Check it out here: {url}"
                    send_email(subject, body, TO_EMAIL)
            
            except Exception as e:
                print(f"Error scraping or inserting data for product: {name} - {e}")
    
    except Exception as e:
        print(f"Error fetching unique products from the database - {e}")
    
    finally:
        # Close the database connection
        conn.close()
        print("Database connection closed.")

def send_email(subject, body, to_email=TO_EMAIL):
    from_email = EMAIL_USER
    password = EMAIL_PASS
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, "plain"))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def fetch_latest_price(conn, product_name):
    cursor = conn.cursor()
    cursor.execute("""
            SELECT price FROM product_database
            WHERE name = ?
            ORDER BY timestamp DESC
            LIMIT 1
                    """, (product_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None
