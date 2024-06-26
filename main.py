from database import create_connection, create_table, insert_product_data, delete_product_data, clear_table
from functions import connect_sql_to_pandas, fetch_all_products, fetch_all_unique_products, plot_price_history, display_available_products_df, automation
from scraper import ProductScraper
import pandas as pd
import matplotlib.pyplot as plt
import schedule
import time
import threading
from app import app

stop_loop = False

def run_scheduler():
    while not stop_loop:
        schedule.run_pending()
        time.sleep(1)

def get_input():
    global stop_loop
    while True:
        user_input = input('Type "stop" to end program: ').lower()
        if user_input == 'stop':
            stop_loop = True
            break

if __name__ == "__main__":
    # Ensure the database and table are set up
    conn = create_connection()
    create_table(conn)
    conn.close()

    # Schedule the automation function to run every Sunday at 00:00
    schedule.every().sunday.at("00:00").do(automation)

    # Start the scheduler in a background thread
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()

    # Start the Flask app
    app.run(debug=True)

    # Wait for the scheduler thread to complete (this will effectively keep the main thread alive)
    scheduler_thread.join()

    # # Ensure the database and table are set up
    # conn = create_connection()
    # create_table(conn)

    # # Clear the table (optional, for testing purposes)
    # # clear_table(conn)

    # # Get URL input from the user
    # user_input = input("Enter the Newegg product URL (type 'No' if there is no URL you want to add): ")

    # if user_input.lower() == 'no':
    #     # If user inputs 'No', skip adding a new product and display existing products
    #     all_products = fetch_all_unique_products(conn)
    #     print(all_products)
    #     pass
    # else:
    #     # If user inputs a URL, attempt to scrape the product data
    #     url = user_input
    #     try:
    #         # Scrape product data
    #         scraper = ProductScraper(url)
    #         scraper.fetch_product_data()

    #         # Insert product data into the database and get the assigned ID
    #         inserted_id = insert_product_data(conn, scraper)
    #         scraper.id = inserted_id  # Set the ID attribute of the scraper object

    #         # Verify the insertion by fetching all products (optional)
    #         # print("Products after insertion:")
    #         # all_products = fetch_all_unique_products(conn)
    #         # print(all_products)

    #     except Exception as e:
    #         # Handle any errors that occur during scraping
    #         print(f'Invalid URL or error scraping data: {str(e)}')

    # # for debugging purposes
    # # dataframe = connect_sql_to_pandas(conn)
    # # print(dataframe)

    # # Display available products
    # product_names = display_available_products_df(conn)

    # # Get product ID input from the user for plotting specific price history
    # try:
    #     chosen_product_id = int(input('Input the ID of the product you want to see the price history plot of: '))
    #     plot_price_history(conn, product_names[chosen_product_id])
    # except ValueError or Exception as e:
    #     print('Alright no plot will be shown :(')

    # products = fetch_all_unique_products(conn)
    
    # # Close the connection
    # conn.close()

    # # Schedule the automation function to run every Sunday at 00:00
    # schedule.every().sunday.at("00:00").do(automation)

    # # Start the input thread
    # input_thread = threading.Thread(target=get_input)
    # input_thread.daemon = True
    # input_thread.start()

    # # Main loop to check for scheduled tasks and handle stopping the loop
    # while True:
    #     schedule.run_pending()
    #     if stop_loop:
    #         break
    #     time.sleep(30)  # Wait for thirty seconds before checking again
