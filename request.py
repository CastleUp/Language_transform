import config_prod
import psycopg2
import pandas as pd

# Функция для подключения к базе данных
def connect_to_db():    
    conn = psycopg2.connect(
        dbname=config_prod.DB_NAME, 
        user=config_prod.DB_USER, 
        password=config_prod.DB_PASSWORD, 
        host=config_prod.DB_HOST,
        port=config_prod.DB_PORT
    )
    return conn

# Функция для выполнения SQL-запроса
def fetch_data_from_db(conn):
    query = """
    SELECT name_ru FROM dict_budget_regions 
    WHERE beg_date <= '2024-09-01' AND end_date >= '2024-09-01'
    AND code LIKE '30%'
    """
    df = pd.read_sql_query(query, conn)
    return df['name_ru'].tolist()  # Возвращаем данные в виде списка

def main():
    conn = connect_to_db()
    districts_ru = fetch_data_from_db(conn)
    print(districts_ru)

if __name__ == "__main__":
    main()