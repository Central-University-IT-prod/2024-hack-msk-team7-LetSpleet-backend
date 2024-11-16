import psycopg2
from core.config import CONFIG



def erase_db():
    conn = psycopg2.connect(
            database=CONFIG.db_name,
            user=CONFIG.user,
            password=CONFIG.password,
            host=CONFIG.host,
            port=CONFIG.port
                    
            )
    cursor = conn.cursor()
    sql_drop_tables = '''DROP TABLE "user", "event", "duty", "receipt"'''
    cursor.execute(sql_drop_tables)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    erase_db()
