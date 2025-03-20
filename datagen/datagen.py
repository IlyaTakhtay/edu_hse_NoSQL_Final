from pymongo import MongoClient
from faker import Faker
import random
import os
from datetime import datetime

MONGO_HOST = os.environ.get("MONGO_HOST", "mongo")
MONGO_PORT = os.environ.get("MONGO_PORT", "27017")
MONGO_USER = os.environ.get("MONGO_INITDB_ROOT_USERNAME", "root")
MONGO_PASS = os.environ.get("MONGO_INITDB_ROOT_PASSWORD", "root")
MONGO_DB = os.environ.get("MONGO_DB", "university_db")


# Подключение к MongoDB
client: MongoClient = MongoClient(f'mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/')
db = client[f"{MONGO_DB}"]

fake = Faker()

# Генерация студентов
def generate_students(count=100):
    students = []
    for _ in range(count):
        student = {
            "_id": fake.uuid4(),  # Номер зачетки
            "full_name": fake.name(),  # ФИО студента
            "group": fake.bothify(text='??-##', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ'),  # Группа
            "enrollment_year": random.randint(2018, 2024),  # Год поступления
            "contacts": {
                "email": fake.email(),  # Email студента
                "phone": fake.phone_number()  # Телефон студента
            }
        }
        students.append(student)
    return students

# Генерация оценок (с вложением курса и преподавателя)
def generate_marks(students, count=200):
    marks = []
    for _ in range(count):
        student = random.choice(students)
        mark = {
            "_id": fake.uuid4(),  # Уникальный идентификатор оценки
            "student_id": student["_id"],  # Номер зачетки студента
            "grade": random.randint(2, 5),  # Оценка (от 2 до 5)
            "type": random.choice(["кр1", "кр2", "экз"]),  # Тип оценки (кр1, кр2, экз и т.д.)
            "course": {
                "name": fake.catch_phrase(),  # Название курса
                "professor": {
                    "full_name": fake.name()  # ФИО преподавателя
                },
                "semester": random.choice(["Fall 2024", "Spring 2025"]),  # Семестр
                "credits": random.randint(1, 10)  # Количество кредитов курса
            }
        }
        marks.append(mark)
    return marks

# Генерация и вставка данных в базу данных
students = generate_students()
marks = generate_marks(students)

db.Student.insert_many(students)
db.Mark.insert_many(marks)

print("Данные успешно сгенерированы и вставлены в базу данных.")
