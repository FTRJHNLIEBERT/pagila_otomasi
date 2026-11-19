import psycopg2

from psycopg2.extras import RealDictCursor

def main():
    create() 
    extract()
    transform_load()   

# ======================= connection =======================

def connection(dbname):
    dsn = f"host=localhost port=5433 user=postgres password=postgres dbname={dbname}"
    conn = psycopg2.connect(dsn, cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    return conn, cursor

# ======================= create =======================

def create():
    conn_otomasi, cursor_otomasi = connection('pagila_otomasi')
    
    # Prepare schema
    create_staging(conn_otomasi, cursor_otomasi)
    create_dw(conn_otomasi, cursor_otomasi) 
    
    # Create staging table
    create_staging_customer(conn_otomasi, cursor_otomasi)
    
    # Create staging table
    create_staging_film(conn_otomasi, cursor_otomasi)
    
    # Create staging  payment
    create_staging_payment(conn_otomasi, cursor_otomasi)
    
    #Create staging rental
    create_staging_rental(conn_otomasi, cursor_otomasi)
    
    #Create staging inventory
    create_staging_inventory(conn_otomasi, cursor_otomasi)
    
    #Create staging store
    create_staging_store(conn_otomasi, cursor_otomasi)
    
    #create table address
    create_staging_address(conn_otomasi, cursor_otomasi)
# ======================= extract =======================
    
def extract():
    conn_pagila, cursor_pagila = connection('pagila')
    conn_po, cursor_po = connection('pagila_otomasi')
    
    # check and insert data customer
    data_customer = extract_table_customer(conn_pagila, cursor_pagila)
    insert_data_customer(conn_po, cursor_po, data_customer)
    
    # check and insert data film
    data_film = extract_table_film(conn_pagila, cursor_pagila)
    insert_data_film(conn_po, cursor_po, data_film)
    
    # check and insert data payment
    data_payment = extract_table_payment(conn_pagila, cursor_pagila)
    insert_data_payment(conn_po, cursor_po, data_payment)
    
    # check and insert data rental
    data_rental = extract_table_rental(conn_pagila, cursor_pagila)
    insert_data_rental(conn_po, cursor_po, data_rental)
    
    #Check and insert data inventory
    data_inventory = extract_table_inventory(conn_pagila, cursor_pagila)
    insert_data_inventory(conn_po, cursor_po, data_inventory)
    
    #check and insert stoer
    data_store = extract_table_store(conn_pagila, cursor_pagila)
    insert_data_store(conn_po, cursor_po, data_store)
    
    #check and insert address
    data_address = extract_table_address(conn_pagila, cursor_pagila)
    insert_data_address(conn_po, cursor_po, data_address)

# ======================= transform - load =======================

def transform_load():
    conn_po, cursor_po = connection('pagila_otomasi')
    
    # transform & load data customer
    transform_load_customer(conn_po, cursor_po)    

# ======================= create schema staging & dw =======================

def create_staging(conn, cursor):
    query = "CREATE SCHEMA IF NOT EXISTS staging"
    cursor.execute(query)
    conn.commit()

def create_dw(conn, cursor):
    query = "CREATE SCHEMA IF NOT EXISTS dw"
    cursor.execute(query)
    conn.commit()

# ======================= create table staging =======================

def create_staging_customer(conn, cursor):
    query = """
    CREATE TABLE IF NOT EXISTS 
        staging.stg_customer (
            customer_id INTEGER,
            first_name VARCHAR(45),
            last_name VARCHAR(45),
            email VARCHAR(50),
            batch_id VARCHAR(30),
            extract_time TIMESTAMP
        ) 
    """
    cursor.execute(query)
    conn.commit()

def create_staging_film(conn, cursor):
    query = """
    CREATE TABLE IF NOT EXISTS staging.stg_film (
            film_id INTEGER,
            title VARCHAR(255),
            rental_rate NUMERIC(4,2),
            batch_id VARCHAR(30),
            extract_time TIMESTAMP
        )
    """
    cursor.execute(query)
    conn.commit()
    
def create_staging_payment(conn, cursor):
    query = """
    CREATE TABLE IF NOT EXISTS staging.stg_payment (
        payment_id INTEGER,
        customer_id INTEGER,
        rental_id INTEGER,
        amount NUMERIC(5,2),
        payment_date TIMESTAMP,
        batch_id VARCHAR(30),
        extract_time TIMESTAMP
    );
    """
    cursor.execute(query)
    conn.commit()
    
def create_staging_rental(conn, cursor):
    query = """
    CREATE TABLE IF NOT EXISTS staging.stg_rental (
        rental_id INTEGER,
        inventory_id INTEGER,
        batch_id VARCHAR(30),
        extract_time TIMESTAMP
    );
    """
    cursor.execute(query)
    conn.commit()
    
def create_staging_inventory(conn, cursor):
    query = """
    CREATE TABLE IF NOT EXISTS staging.stg_inventory (
        inventory_id INTEGER,
        film_id INTEGER,
        store_id INTEGER,
        batch_id VARCHAR(30),
        extract_time TIMESTAMP
    );
    """
    cursor.execute(query)
    conn.commit()
    
def create_staging_store(conn, cursor):
    query = """
    CREATE TABLE IF NOT EXISTS staging.stg_store (
        store_id INTEGER,
        address_id INTEGER,
        batch_id VARCHAR(30),
        extract_time TIMESTAMP
    );
    """
    cursor.execute(query)
    conn.commit()
    
def create_staging_address(conn, cursor):
    query = """
    CREATE TABLE staging.stg_address (
        address_id INTEGER,
        address VARCHAR(50),
        batch_id VARCHAR(30),
        extract_time TIMESTAMP
    );
    """
    cursor.execute(query)
    conn.commit()

    
# ======================= extract table staging =======================
    
def extract_table_customer(conn_pagila, cursor_pagila):
    query = """
    SELECT
        customer_id,
        first_name,
        last_name,
        email,
        %s,
        CURRENT_TIMESTAMP
    FROM public.customer"""
    
    cursor_pagila.execute(query, ('B001',))
    conn_pagila.commit()
    
    return cursor_pagila.fetchall()

def extract_table_film(conn_pagila, cursor_pagila):
    query = """
    SELECT
        film_id,
        title,
        rental_rate,
        %s,
        CURRENT_TIMESTAMP
    FROM public.film"""
        
    cursor_pagila.execute(query, ('B001',))
    conn_pagila.commit()
        
    return cursor_pagila.fetchall()

def extract_table_payment(conn_pagila, cursor_pagila):
    query = """
    SELECT
        payment_id,
        customer_id,
        rental_id,
        amount,
        payment_date,
        %s,
        CURRENT_TIMESTAMP
    FROM public.payment"""
        
    cursor_pagila.execute(query, ('B001',))
    conn_pagila.commit()
        
    return cursor_pagila.fetchall()

def extract_table_rental(conn_pagila, cursor_pagila):
    query = """
    SELECT
        rental_id,
        inventory_id,
        %s,
        CURRENT_TIMESTAMP
    FROM public.rental"""
        
    cursor_pagila.execute(query, ('B001',))
    conn_pagila.commit()
        
    return cursor_pagila.fetchall()

def extract_table_inventory(conn_pagila, cursor_pagila):
    query = """
    SELECT
        inventory_id,
        film_id,
        store_id,
        %s,
        CURRENT_TIMESTAMP
    FROM public.inventory"""
        
    cursor_pagila.execute(query, ('B001',))
    conn_pagila.commit()
        
    return cursor_pagila.fetchall()


def extract_table_store(conn_pagila, cursor_pagila):
    query = """
    SELECT
        store_id,
        address_id,
        %s,
        CURRENT_TIMESTAMP
    FROM public.store"""
        
    cursor_pagila.execute(query, ('B001',))
    conn_pagila.commit()
        
    return cursor_pagila.fetchall()

def extract_table_address(conn_pagila, cursor_pagila):
    query = """
    SELECT
        address_id,
        address,
        %s,
        CURRENT_TIMESTAMP
    FROM public.address"""
        
    cursor_pagila.execute(query, ('B001',))
    conn_pagila.commit()
        
    return cursor_pagila.fetchall()


    
# ======================= insert table staging =======================

def insert_data_customer(conn_po, cursor_po, data_customer):
    # check table customer by batch_id before inserting the data
    query_check = "SELECT * FROM staging.stg_customer WHERE batch_id = %s"
    cursor_po.execute(query_check, ('B001',))
    
    # if customer data is not exist
    if cursor_po.rowcount == 0:
        # do iteration (loop) for each row data
        for item in data_customer:
            query = """
            INSERT INTO 
                staging.stg_customer (customer_id, first_name, 
                last_name, email, batch_id, extract_time)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor_po.execute(query, (
                item['customer_id'], item['first_name'], item['last_name'],
                item['email'], 'B001', 'NOW()'
            ))
            conn_po.commit()

def insert_data_film(conn_po, cursor_po, data_film):
    # check table film by batch_id before inserting the data
    query_check = "SELECT * FROM staging.stg_film WHERE batch_id = %s"
    cursor_po.execute(query_check, ('B001',))
        
    # if film data is not exist
    if cursor_po.rowcount == 0:
        # do iteration (loop) for each row data
        for item in data_film:
            query = """
            INSERT INTO 
                staging.stg_film (film_id,
                title, rental_rate, batch_id, extract_time)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor_po.execute(query, (
                item['film_id'], item['title'], item['rental_rate'],
                'B001', 'NOW()'
            ))
            conn_po.commit()
            
def insert_data_payment(conn_po, cursor_po, data_payment):
    # check table payment by batch_id before inserting the data
    query_check = "SELECT * FROM staging.stg_payment WHERE batch_id = %s"
    cursor_po.execute(query_check, ('B001',))
    
    # if payment data is not exist
    if cursor_po.rowcount == 0:
        # do iteration (loop) for each row data
        for item in data_payment:
            query = """
            INSERT INTO 
                staging.stg_payment (payment_id, customer_id,
                rental_id, amount, payment_date, batch_id, extract_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor_po.execute(query, (
                item['payment_id'], item['customer_id'], item['rental_id'],
                item['amount'], item['payment_date'], 'B001', 'NOW()'
            ))
            conn_po.commit()
            
def insert_data_rental (conn_po, cursor_po, data_rental):
    # check table rental by batch_id before inserting the data
    query_check = "SELECT * FROM staging.stg_rental WHERE batch_id = %s"
    cursor_po.execute(query_check, ('B001',))
    
    # if rental data is not exist
    if cursor_po.rowcount == 0:
        # do iteration (loop) for each row data
        for item in data_rental:
            query = """
            INSERT INTO 
                staging.stg_rental (rental_id, inventory_id,
                batch_id, extract_time)
            VALUES (%s, %s, %s, %s)
            """
            cursor_po.execute(query, (
                item['rental_id'], item['inventory_id'],
                'B001', 'NOW()'
            ))
            conn_po.commit()
            
def insert_data_inventory (conn_po, cursor_po, data_inventory):
    # check table inventory by batch_id before inserting the data
    query_check = "SELECT * FROM staging.stg_inventory WHERE batch_id = %s"
    cursor_po.execute(query_check, ('B001',))
    
    # if inventory data is not exist
    if cursor_po.rowcount == 0:
        # do iteration (loop) for each row data
        for item in data_inventory:
            query = """
            INSERT INTO 
                staging.stg_inventory (inventory_id, film_id,
                store_id, batch_id, extract_time)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor_po.execute(query, (
                item['inventory_id'], item['film_id'], item['store_id'],
                'B001', 'NOW()'
            ))
            conn_po.commit()
            
def insert_data_store (conn_po, cursor_po, data_store):
    # check table store by batch_id before inserting the data
    query_check = "SELECT * FROM staging.stg_store WHERE batch_id = %s"
    cursor_po.execute(query_check, ('B001',))
    
    # if store data is not exist
    if cursor_po.rowcount == 0:
        # do iteration (loop) for each row data
        for item in data_store:
            query = """
            INSERT INTO 
                staging.stg_store (store_id, address_id,
                batch_id, extract_time)
            VALUES (%s, %s, %s, %s)
            """
            cursor_po.execute(query, (
                item['store_id'], item['address_id'],
                'B001', 'NOW()'
            ))
            conn_po.commit()
            
def insert_data_address (conn_po, cursor_po, data_address):
    # check table address by batch_id before inserting the data
    query_check = "SELECT * FROM staging.stg_address WHERE batch_id = %s"
    cursor_po.execute(query_check, ('B001',))
    
    # if address data is not exist
    if cursor_po.rowcount == 0:
        # do iteration (loop) for each row data
        for item in data_address:
            query = """
            INSERT INTO 
                staging.stg_address (address_id, address,
                batch_id, extract_time)
            VALUES (%s, %s, %s, %s)
            """
            cursor_po.execute(query, (
                item['address_id'], item['address'],
                'B001', 'NOW()'
            ))
            conn_po.commit()

# ======================= transform data & load customer =======================

#customer
def transform_load_customer(conn_po, cursor_po):
    query_drop = "DROP TABLE IF EXIST dw.dim_customer"
    cursor_po.execute(query_drop)
    conn_po.commit()
    
    query = """
        INSERT INTO dw.dim_customer (
        customer_id,
        first_name,
        last_name,
        full_name,
        email
    )
    SELECT
        customer_id,
        INITCAP(TRIM(first_name)) AS first_name,
        INITCAP(TRIM(last_name)) AS last_name,
        CONCAT_WS(
            ' ',
            INITCAP(TRIM(first_name)),
            INITCAP(TRIM(last_name))
        ),
        LOWER(TRIM(email)) AS full_name
    FROM staging.stg_customer
    """
    
    cursor_po.execute(query)
    conn_po.commit()
    
def transform_load_film(conn_po, cursor_po):
    query_drop = "DROP TABLE IF EXIST dw.dim_film"
    cursor_po.execute(query_drop)
    conn_po.commit()
    
    query = """
        INSERT INTO dw.dim_film (
        film_id,
        title,
        rental_rate
    )
    SELECT
        film_id,
        TRIM(title),
        rental_rate
    FROM staging.stg_film;
    """
    
    cursor_po.execute(query)
    conn_po.commit()
    
    
def transform_load_store(conn_po, cursor_po):
    query_drop = "DROP TABLE IF EXIST dw.dim_store"
    cursor_po.execute(query_drop)
    conn_po.commit()
    
    query = """
        INSERT INTO dw.dim_store (
        store_id,
        address_id
    )
    SELECT
        s.store_id,
        TRIM(a.address)
    FROM staging.stg_store s
    JOIN staging.stg_address a
        ON s.address_id = a.address_id;
    """
    cursor_po.execute(query)
    conn_po.commit()
    
def transform_load_date(conn_po, cursor_po):
    query_drop = "DROP TABLE IF EXIST dw.dim_date"
    cursor_po.execute(query_drop)
    conn_po.commit()
        
    query = """
        INSERT INTO dw.dim_date (
        date_key,
        full_date,
        day,
        month,
        quarter,
        year
    )
    SELECT DISTINCT
        TO_CHAR(payment_date, 'YYYYMMDD')::INTEGER,
        payment_date::DATE,
        EXTRACT(DAY FROM payment_date)::INTEGER,
        EXTRACT(MONTH FROM payment_date)::INTEGER,
        EXTRACT(QUARTER FROM payment_date)::INTEGER,
        EXTRACT(YEAR FROM payment_date)::INTEGER
    FROM staging.stg_payment
    WHERE payment_date IS NOT NULL;
    """ 
    
    cursor_po.execute(query)
    conn_po.commit()

#payment

def transform_load_payment(conn_po, cursor_po):
    query_drop = "DROP TABLE IF EXIST dw.fact_payment"
    cursor_po.execute(query_drop)
    conn_po.commit()
    
    query = """
        INSERT INTO dw.fact_payment (
        payment_id,
        customer_key,
        film_key,
        store_key,
        revenue_amount
    )
    SELECT
        p.payment_id,
        d.date_key,
        c.customer_key,
        f.film_key,
        s.store_key,
        p.amount
    FROM staging.stg_payment p
    JOIN staging.stg_rental r
        ON p.rental_id = r.rental_id
    JOIN staging.stg_inventory i
        ON r.inventory_id = i.inventory_id
    JOIN dw.dim_date d
        ON p.payment_date::DATE = d.full_date
    JOIN dw.dim_customer c
        ON p.customer_id = c.customer_id
    JOIN dw.dim_film f
        ON i.film_id = f.film_id
    JOIN dw.dim_store s
        ON i.store_id = s.store_id;
    """
    
    cursor_po.execute(query)
    conn_po.commit()

    
    
    

    
    


if __name__ == '__main__':
    # 1. run 'python.exe (atau py.exe) etl.py
    # 2. pastikan bahwa tabel telah di insert / table dibuat
    main()