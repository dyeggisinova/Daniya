import psycopg2

name = input("Введите имя: ")
phone = input("Введите номер телефона: ")

conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    host="localhost",
    port="5432"
)

cur = conn.cursor()
cur.execute("INSERT INTO phonebook (name, phone) VALUES (%s, %s)", (name, phone))
conn.commit()

print("Контакт добавлен!")
cur.close()
conn.close()
