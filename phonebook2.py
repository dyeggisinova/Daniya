import psycopg2
import csv

# Подключение к базе данных
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Создание таблицы
cur.execute("""
CREATE TABLE IF NOT EXISTS phonebook (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL
);
""")
conn.commit()

# 1. Загрузка из CSV-файла
def insert_from_csv(filename):
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cur.execute(
                "INSERT INTO phonebook (name, phone) VALUES (%s, %s)",
                (row['name'], row['phone'])
            )
    conn.commit()




# 2. Ввод вручную
def insert_from_input():
    name = input("Введите имя: ")
    phone = input("Введите номер телефона: ")
    cur.execute("INSERT INTO phonebook (name, phone) VALUES (%s, %s)", (name, phone))
    conn.commit()

# Обновление данных
def update_data():
    what = input("Что вы хотите изменить? (name/phone): ")
    target = input("Введите текущее имя или номер: ")
    new_value = input("Введите новое значение: ")
    if what == "name":
        cur.execute("UPDATE phonebook SET name = %s WHERE phone = %s", (new_value, target))
    elif what == "phone":
        cur.execute("UPDATE phonebook SET phone = %s WHERE name = %s", (new_value, target))
    conn.commit()

# Фильтрация данных
def filter_data():
    search = input("Введите имя или часть имени для поиска: ")
    cur.execute("SELECT * FROM phonebook WHERE name ILIKE %s", ('%' + search + '%',))
    results = cur.fetchall()
    for row in results:
        print(row)

def show_all():
    cur.execute("SELECT * FROM phonebook")
    results = cur.fetchall()
    for row in results:
        print(row)


# Удаление по имени или номеру
def delete_data():
    by = input("Удалить по (name/phone): ")
    value = input("Введите значение: ")
    if by == "name":
        cur.execute("DELETE FROM phonebook WHERE name = %s", (value,))
    elif by == "phone":
        cur.execute("DELETE FROM phonebook WHERE phone = %s", (value,))
    conn.commit()

# Меню
while True:
    print("\n1. Загрузить из CSV")
    print("2. Ввести вручную")
    print("3. Обновить данные")
    print("4. Поиск")
    print("5. Удалить")
    print("6. Показать все запис")
    print("7. Выход")

    choice = input("Выберите действие: ")

    if choice == '1':
        filename = input("Введите имя CSV-файла: ")
        insert_from_csv(filename)
    elif choice == '2':
        insert_from_input()
    elif choice == '3':
        update_data()
    elif choice == '4':
        filter_data()
    elif choice == '5':
        delete_data()
    elif choice == '6':
        show_all()
    elif choice =='7':
        break
    else:
        print("Неверный выбор!")

# Закрытие соединения
cur.close()
conn.close()
