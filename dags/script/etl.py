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

def insert_data_film(conn_po, cursor_po, data_customer):
    # check table film by batch_id before inserting the data
    query_check = "SELECT * FROM staging.stg_film WHERE batch_id = %s"
    cursor_po.execute(query_check, ('B001',))
        
    # if film data is not exist
    if cursor_po.rowcount == 0:
        # do iteration (loop) for each row data
        for item in data_customer:
            query = """
            INSERT INTO 
                staging.stg_customer (film_id,
                title, rental_rate, batch_id, extract_time)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor_po.execute(query, (
                item['film_id'], item['title'], item['rental_rate'],
                'B001', 'NOW()'
            ))
            conn_po.commit()
    

# ======================= transform data & load customer =======================

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


if __name__ == '__main__':
    # 1. run 'python.exe (atau py.exe) etl.py
    # 2. pastikan bahwa tabel telah di insert / table dibuat
    main()