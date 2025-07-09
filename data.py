from datetime import datetime

# Это наша "база данных" в памяти (просто списки)
# Версии опросника
versions = [
    {"id": 1, "name": "v1.0", "created_at": datetime.utcnow().isoformat()}
]

# Вопросы из Excel-таблицы (листы ОП и ОЛ_вэб)
questions = [
    {
        "id": 1,
        "version_id": 1,
        "number": "1.1",
        "text": "Наименование объекта",
        "type": "dropdown",
        "options": ["Жилой дом", "Коммерческое здание"],
        "constraints": None
    },
    {
        "id": 2,
        "version_id": 1,
        "number": "1.2",
        "text": "Адрес объекта",
        "type": "text",
        "options": None,
        "constraints": None
    },
    {
        "id": 3,
        "version_id": 1,
        "number": "1.4",
        "text": "Класс комфорта",
        "type": "dropdown",
        "options": ["Стандарт", "Комфорт", "Комфорт+", "Бизнес", "Премиум", "Элит"],
        "constraints": None
    },
    {
        "id": 4,
        "version_id": 1,
        "number": "1.7",
        "text": "Сейсмичность региона строительства",
        "type": "dropdown",
        "options": ["10 баллов", "9 баллов", "8 баллов", "7 баллов", "менее 7 баллов"],
        "constraints": {"default": "менее 7 баллов"}  # По умолчанию для Москвы
    },
    {
        "id": 5,
        "version_id": 1,
        "number": "1.8",
        "text": "Площадь участка строительства, м²",
        "type": "integer",
        "options": None,
        "constraints": {"min": 1}  # Не меньше 1
    },
    {
        "id": 6,
        "version_id": 1,
        "number": "1.12",
        "text": "Тип фундамента",
        "type": "dropdown",
        "options": ["Свайный фундамент", "Монолитная плита на естественном основании"],
        "constraints": None
    },
    {
        "id": 7,
        "version_id": 1,
        "number": "2.1",
        "text": "Количество корпусов",
        "type": "integer",
        "options": None,
        "constraints": {"min": 1, "max": 20}  # От 1 до 20
    },
    {
        "id": 8,
        "version_id": 1,
        "number": "2.1.1",
        "text": "Выберите корпуса на общей плите",
        "type": "dropdown",
        "options": [],  # Будет заполняться в зависимости от 2.1
        "constraints": None
    },
    {
        "id": 9,
        "version_id": 1,
        "number": "2.2",
        "text": "Количество стилобатов",
        "type": "integer",
        "options": None,
        "constraints": {"min": 0, "max_ref": "2.1"}  # Зависит от 2.1
    }
]

# Ответы пользователей
responses = []

# Функции для работы с данными
def find_version(version_id: int):
    """Ищет версию по ID"""
    for version in versions:
        if version["id"] == version_id:
            return version
    return None

def find_question(question_id: int):
    """Ищет вопрос по ID"""
    for question in questions:
        if question["id"] == question_id:
            return question
    return None

def get_questions_for_version(version_id: int):
    """Возвращает все вопросы для версии"""
    return [q for q in questions if q["version_id"] == version_id]

def get_user_response(user_id: int, version_id: int, question_number: str):
    """Ищет ответ пользователя по номеру вопроса"""
    for r in responses:
        question = find_question(r["question_id"])
        if (r["user_id"] == user_id and 
            r["version_id"] == version_id and 
            question["number"] == question_number):
            return r
    return None