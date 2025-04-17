import psycopg2

conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    host="localhost",
    port="5432"
)

cur = conn.cursor()
cur.execute("SELECT * FROM phonebook")
rows = cur.fetchall()

for row in rows:
    print(f"ID: {row[0]}, Имя: {row[1]}, Телефон: {row[2]}")

cur.close()
conn.close()
