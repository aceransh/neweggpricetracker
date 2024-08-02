from flask import render_template, request, redirect, url_for, flash
from app import app, db
from database import create_connection, insert_product_data, delete_product_data, create_table
from functions import fetch_all_products, fetch_latest_price, plot_price_history, send_email, automation
from scraper import ProductScraper
import schedule
import time
import threading

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            return "Email is required!", 400  # Bad request
        print(f"Received email: {email}")
        return redirect(url_for('submit_product'))

    return render_template('index.html')

@app.route('/submit_product', methods=['GET', 'POST'])
def submit_product():
    if request.method == 'POST':
        url = request.form.get('url')
        print(f"Received URL: {url}")  # Debug statement
        if not url:
            print("No URL provided.")  # Debug statement
            return "URL is required!", 400  # Bad request

        try:
            print("Initializing scraper...")  # Debug statement
            scraper = ProductScraper(url)
            scraper.fetch_product_data()
            print(f"Product data fetched: {scraper.return_product_data()}")  # Debug statement

            conn = create_connection()
            print("Database connection established.")  # Debug statement
            insert_product_data(conn, scraper)
            print("Product data inserted into database.")  # Debug statement
            conn.close()
            print("Database connection closed.")  # Debug statement

            return redirect(url_for('submit_product'))
        except Exception as e:
            print(f"Error occurred: {str(e)}")  # Debug statement
            flash(f"Error: {str(e)}", "danger")
            return redirect(url_for('submit_product'))

    conn = create_connection()
    products = fetch_all_products(conn)
    conn.close()
    print(f"Fetched products: {products}")  # Debug statement
    return render_template('submit_product.html', products=products)

@app.route('/delete_product/<int:id>', methods=['POST'])
def delete_product(id):
    try:
        conn = create_connection()
        delete_product_data(conn, id)
        conn.close()
        flash("Product deleted successfully!", "success")
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
    return redirect(url_for('submit_product'))

@app.route('/check_price_now/<int:id>', methods=['POST'])
def check_price_now(id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, url FROM product_database WHERE id=?", (id,))
    product = cursor.fetchone()
    if product:
        try:
            scraper = ProductScraper(product[1])
            scraper.fetch_product_data()
            insert_product_data(conn, scraper)
            flash("Price checked successfully!", "success")
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
    conn.close()
    return redirect(url_for('submit_product'))

@app.route('/display_price_history/<int:id>', methods=['GET'])
def display_price_history(id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM product_database WHERE id=?", (id,))
    product = cursor.fetchone()
    if product:
        image_path = plot_price_history(conn, product[0])
        if image_path:
            conn.close()
            return render_template('show_price_history.html', image_path=image_path, product_name=product[0])
    conn.close()
    return redirect(url_for('submit_product'))

# Schedule the price check
schedule.every().sunday.at("00:00").do(automation)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

if __name__ == '__main__':
    conn = create_connection()
    if conn is not None:
        create_table(conn)
        conn.close()
    app.run(debug=True)
