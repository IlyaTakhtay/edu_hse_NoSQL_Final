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

# Списки для генерации данных
FACULTIES = [
    "Информационные технологии",
    "Экономика",
    "Юриспруденция",
    "Международные отношения",
    "Бизнес и менеджмент",
    "Социология",
    "Психология",
    "Филология",
    "Математика",
    "Физика",
    "История",
    "Философия",
    "Дизайн",
    "Журналистика",
    "Политология"
]

POSITIONS = [
    "Профессор",
    "Доцент",
    "Ассистент",
    "Старший преподаватель",
    "Преподаватель"
]

DEPARTMENTS = [
    "Кафедра программирования",
    "Кафедра математики и статистики",
    "Кафедра экономической теории",
    "Кафедра права и законодательства",
    "Кафедра международных исследований",
    "Кафедра менеджмента и маркетинга",
    "Кафедра социологии и социальных исследований",
    "Кафедра психологии развития",
    "Кафедра филологии и лингвистики",
    "Кафедра физики и нанотехнологий"
]

# Генерация студентов
def generate_students(count=100):
    students = []
    for _ in range(count):
        student = {
            "_id": fake.uuid4(),
            "name": fake.name(),
            "group": fake.bothify(text='??-##', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
            "faculty": random.choice(FACULTIES),
            "year": random.randint(1, 6)
        }
        students.append(student)
    return students

# Генерация преподавателей
def generate_teachers(count=20):
    teachers = []
    for _ in range(count):
        teacher = {
            "_id": fake.uuid4(),
            "fullName": fake.name(),
            "department": random.choice(DEPARTMENTS),
            "position": random.choice(POSITIONS),
            "email": fake.email()
        }
        teachers.append(teacher)
    return teachers

# Генерация курсов
def generate_courses(teachers, count=20):
    courses = []
    for _ in range(count):
        course = {
            "_id": fake.uuid4(),
            "name": fake.catch_phrase(),
            "department": random.choice(DEPARTMENTS),
            "credits": random.randint(1, 10),
            "mainTeacher": random.choice(teachers)["_id"]
        }
        courses.append(course)
    return courses


# Генерация ведомостей
def generate_grade_sheets(courses, students, count=40):
    grade_sheets = []
    for _ in range(count):
        course = random.choice(courses)
        is_graded = random.choice([True, False])
        future_date = fake.date_between(start_date="+1y", end_date="+2y")
        grade_sheet = {
            "_id": fake.uuid4(),
            "courseId": course["_id"],
            "semester": random.choice(["Fall 2025", "Spring 2026"]),
            "teacherId": course["mainTeacher"],
            "date": datetime.combine(future_date, datetime.min.time()),
            "status": "closed" if is_graded else "open",
            "grades": []
        }
        if is_graded:
            for student in random.sample(students, random.randint(20,30)):
                future_date = fake.date_between(start_date="+1y", end_date="+2y")
                grade = {
                    "studentId": student["_id"],
                    "grade": random.randint(2, 5),
                    "date": grade_sheet["date"]
                }
                grade_sheet["grades"].append(grade)
        grade_sheets.append(grade_sheet)
    return grade_sheets

# Генерация и вставка данных
students = generate_students()
teachers = generate_teachers()
courses = generate_courses(teachers)
grade_sheets = generate_grade_sheets(courses, students)

db.students.insert_many(students)
db.teachers.insert_many(teachers)
db.courses.insert_many(courses)
db.gradeSheets.insert_many(grade_sheets)

print("Данные успешно сгенерированы и вставлены в базу данных.")
