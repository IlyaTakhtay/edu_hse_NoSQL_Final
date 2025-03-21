## **Описание структуры базы данных**

База данных состоит из двух основных коллекций: `Student` и `Mark`. Структура денормализована для оптимизации операций чтения, которые являются наиболее частыми в данном сценарии использования. Это позволяет минимизировать количество операций объединения (`JOIN`) и ускорить выполнение запросов.

---

### **1. Коллекция `Student`**

Хранит информацию о студентах, включая их личные данные, группу, год поступления и контактную информацию.

#### Пример документа:

```json
{
  "_id": "64e216ac-f5ec-41ed-bae0-363fdf00f29c",
  "full_name": "Jane Martin",
  "group": "CE-78",
  "enrollment_year": 2024,
  "contacts": {
    "email": "alexisjohnson@example.net",
    "phone": "(943)960-3614x6500"
  }
}
```

#### Поля:

- `_id`: Уникальный идентификатор студента (номер зачетки).
- `full_name`: Полное имя студента.
- `group`: Группа студента.
- `enrollment_year`: Год поступления студента.
- `contacts`: Объект с контактной информацией:
  - `email`: Электронная почта студента.
  - `phone`: Номер телефона студента.

---
#### Схема создания:
```javascript
db.createCollection("student", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["_id", "full_name", "group"],
      properties: {
        _id: {
          bsonType: "string"
        },
        full_name: {
          bsonType: "string"
        },
        group: {
          bsonType: "string"
        },
        enrollment_year: {
          bsonType: "int",
          minimum: 1900,
          maximum: 2100
        },
        contacts: {
          bsonType: "object",
          properties: {
            email: {
              bsonType: "string",
              pattern: "^.+@.+\\..+$"
            },
            phone: {
              bsonType: "string"
            }
          }
        }
      }
    }
  }
});
```
### **2. Коллекция `Mark`**

Хранит информацию об оценках студентов, связанных с конкретными курсами и семестрами.

#### Пример документа:

```json
{
  "_id": "0c7071d2-7c24-445f-9fde-42a69b349e93",
  "student_id": "28d6cf7f-9192-4fb6-8676-444a14921b77",
  "grade": 3,
  "type": "test2",
  "course": {
    "name": "Машинное обучение и анализ данных с помощью Python",
    "duration": "216 часов",
    "semester": "Spring 2025",
    "credits": 3
  },
  "professor": {
    "full_name": "Janet Erickson"
  }
}
```

#### Поля:

- `_id`: Уникальный идентификатор записи об оценке.
- `student_id`: ID студента (ссылка на коллекцию `Student`). - по сути номер зачетки по которому можно незавимо отбирать данные из этих таблиц
- `grade`: Оценка за определённый тип работы.
- `type`: Тип оценки (например, промежуточная работа, тест, проект, итоговая оценка).
- `course`: Объект с информацией о курсе:
  - `name`: Название курса.
  - `duration`: Длительность курса в часах.
  - `semester`: Семестр, в котором проводится курс.
  - `credits`: Количество кредитов за курс.
  - `professor`: Объект с информацией о преподавателе:
    - `full_name`: Полное имя преподавателя.

---
#### Схема создания:
```javascript
db.createCollection("mark", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["_id", "student_id", "grade", "type", "course"],
      properties: {
        _id: {
          bsonType: "string"
        },
        student_id: {
          bsonType: "string"
        },
        grade: {
          bsonType: "int",
          minimum: 1,
          maximum: 10
        },
        type: {
          bsonType: "string",
          enum: ["test1", "test2", "exam", "project"]
        },
        course: {
          bsonType: "object",
          required: ["name"],
          properties: {
            name: {
              bsonType: "string"
            },
            duration: {
              bsonType: "string",
              pattern: "^\\d+ часов$"
            },
            semester: {
              bsonType: "string",
              pattern: "^(Fall|Spring) \\d{4}$"
            },
            credits: {
              bsonType: "int",
              minimum: 1
            }
          }
        },
        professor: {
          bsonType: "object",
          properties: {
            full_name: {
              bsonType:"string"
            }
          }
        }
      }
    }
  }
});
```
## **Обоснование структуры**

1. **Оптимизация запросов на чтение**:
   Денормализованная модель позволяет хранить всю информацию о курсе и преподавателе прямо в документе оценки (`Mark`). Это исключает необходимость дополнительных запросов к коллекциям курсов или преподавателей и ускоряет выполнение аналитических запросов.
   Дополнительная информация о студентах хранится в отдельной коллекци, поскольку она редко требуется, причина - запросы чаще всего происходят по номеру зачетки.
2. **Упрощение аналитики**:
   Вложенные объекты позволяют легко фильтровать данные по конкретным параметрам (например, семестр, название курса, преподаватель).
---

Для обеспечения высокой производительности при выполнении запросов необходимо добавить индексы на ключевые поля:

### **Индексы для коллекции `Student`**

1. Композитный индекс на поле `id + group`:

```javascript
db.Student.createIndex({ _id: 1, group: 1 });
```

Ускоряет выборку студентов по группам. 
2. Индекс на поле `enrollment_year`:

```javascript
db.Student.createIndex({ enrollment_year: 1 });
```

Удобно для фильтрации студентов по году поступления.

---

### **Индексы для коллекции `Mark`**

1. Индекс на поле `student_id`:

```javascript
db.Mark.createIndex({ student_id: 1 });
```

Ускоряет выборку оценок для конкретного студента. 
2. Композитный индекс на поля `course.name` и `course.semester`:

```javascript
db.Mark.createIndex({ "course.name": 1, "course.semester": 1 });
```

Оптимизирует запросы, связанные с курсами за определённый семестр. 
3. Индекс на поле `type`:

```javascript
db.Mark.createIndex({ type: 1 });
```

Ускоряет выборку промежуточных или итоговых оценок. 
4. Композитный индекс на поля `grade` и `course.name`:

```javascript
db.Mark.createIndex({ grade: 1, "course.name": 1 });
```

Полезен для аналитических запросов, например, поиска студентов с оценками ниже порога.

---

## **Примеры запросов**

### **1. Просмотр промежуточных оценок за конкретный семестр у конкретного студента**

```javascript
db.Mark.find({
  student_id: "64e216ac-f5ec-41ed-bae0-363fdf00f29c",
  "course.semester": "Spring 2025",
  type: { $ne: "exam" },
});
```

### **2. Просмотр итоговой оценки за курс у конкретного студента**

```javascript
db.Mark.findOne({
  student_id: "64e216ac-f5ec-41ed-bae0-363fdf00f29c",
  type: "exam",
  "course.name": "Машинное обучение и анализ данных с помощью Python",
});
```

### **3. Просмотр промежуточных оценок всех студентов за текущий семестр**

```javascript
db.Mark.find({
  type: { $ne: "exam" },
  "course.semester": "Spring 2025",
});
```

### **4. Просмотр итоговой оценки всех студентов за текущий семестр**

```javascript
db.Mark.find({
  type: "exam",
  "course.semester": "Spring 2025",
});
```

### **5. Обновление оценки (например, исправление ошибки)**

```javascript
const existingMark = db.Mark.updateOne(
  { student_id: "0c7071d2-7c24-445f-9fde-42a69b349e93", type: "test2" },
  { $set: { grade: 4 } }
);
```

### **6. Добавление итоговой оценки за курс**

```javascript
db.Mark.insertOne({
  student_id: "64e216ac-f5ec-41ed-bae0-363fdf00f29c",
  grade: 5,
  type: "exam",
  course: {
    name: "Машинное обучение и анализ данных с помощью Python",
    duration: "216 часов",
    semester: "Spring 2025",
    credits: 3,
    professor: {
      full_name: "Janet Erickson",
    },
  },
});
```

### **7. Список студентов без промежуточных оценок**

```javascript
const studentIdsWithExam = db.Mark.distinct("student_id", {
  type: "exam",
  "course.semester": "Spring 2025",
});

db.Student.find({
  _id: { $nin: studentIdsWithExam },
});
```

### **8. Список курсов, на которых студент обучается в текущем семестре**

```javascript
db.Mark.find(
  {
    student_id: "64e216ac-f5ec-41ed-bae0-363fdf00f29c", // ID студента
    "course.semester": "Spring 2025", // Текущий семестр
  },
  {
    _id: 0,
    "course.name": 1,
    "course.professor.full_name": 1, // Имя преподавателя
  }
);
```

### **9. Список студентов с оценками выше определённого порога за текущий семестр**

Этот запрос возвращает студентов, которые получили оценки выше указанного значения (например, 8) за текущий семестр.

```javascript
db.Mark.aggregate([
  { $match: { grade: { $gt: 8 }, "course.semester": "Spring 2025" } },
  {
    $lookup: {
      from: "Student",
      localField: "student_id",
      foreignField: "_id",
      as: "student_info",
    },
  },
  {
    $project: {
      "student_info.full_name": 1,
      "student_info.group": 1,
      grade: 1,
      "course.name": 1,
    },
  },
]);
```

### **10. Средний балл каждого студента за текущий семестр**

Этот запрос вычисляет средний балл для каждого студента за указанный семестр.

```javascript
db.Mark.aggregate([
  { $match: { "course.semester": "Spring 2025" } },
  {
    $group: {
      _id: "$student_id",
      average_grade: { $avg: "$grade" },
    },
  },
  {
    $lookup: {
      from: "Student",
      localField: "_id",
      foreignField: "_id",
      as: "student_info",
    },
  },
  {
    $project: {
      "student_info.full_name": 1,
      average_grade: 1,
    },
  },
]);
```
