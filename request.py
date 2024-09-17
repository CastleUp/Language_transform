import config_prod
import pandas as pd
from psycopg2 import connect

# Функция для подключения к базе данных
def connect_to_db():
    conn = connect(
        dbname=config_prod.DB_NAME,
        user=config_prod.DB_USER,
        password=config_prod.DB_PASSWORD,
        host=config_prod.DB_HOST,
        port=config_prod.DB_PORT
    )
    return conn

# Функция для выполнения SQL-запроса и получения данных
def fetch_data_from_db(conn):
    query = """
    SELECT id, code, name_ru, name_kk FROM dict_budget_regions 
    WHERE beg_date <= '2024-09-01' AND end_date >= '2024-09-01'
    AND name_ru IS NOT NULL AND name_kk IS NOT NULL
    """
    df = pd.read_sql_query(query, conn)
    return df

# Функция для создания новой таблицы с результатами
def create_declined_table(conn):
    query = """
    CREATE TABLE IF NOT EXISTS dict_budget_regions_declined (
        id SERIAL PRIMARY KEY,
        code VARCHAR(255),
        name_ru VARCHAR(255),
        name_ru_declined VARCHAR(255),
        name_kk VARCHAR(255),
        name_kk_declined VARCHAR(255)
    );
    """
    with conn.cursor() as cursor:
        cursor.execute(query)
        conn.commit()

# Функция для вставки данных в новую таблицу
def insert_declined_data(conn, data):
    with conn.cursor() as cursor:
        query = """
        INSERT INTO dict_budget_regions_declined (id, code, name_ru, name_ru_declined, name_kk, name_kk_declined)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(query, data)
        conn.commit()

def main():
    conn = connect_to_db()

    # Создаем таблицу для данных с родительным падежом
    create_declined_table(conn)

    # Получаем данные из исходной таблицы
    df = fetch_data_from_db(conn)
    print(df)

    conn.close()

if __name__ == "__main__":
    main()
