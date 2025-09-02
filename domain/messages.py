from enum import Enum

class Messages(Enum):
    VERSION_NOT_FOUND = "Version not found"
    QUESTION_NOT_FOUND = "Question not found"
    RESPONSE_NOT_FOUND = "Response not found"
    INVALID_PAYLOAD = "Invalid payload"

    # Russian translations (optional future use)
    # VERSION_NOT_FOUND_RU = "Версия не найдена"
    # QUESTION_NOT_FOUND_RU = "Вопрос не найден"
    # RESPONSE_NOT_FOUND_RU = "Ответ не найден"
    # INVALID_PAYLOAD_RU = "Некорректные данные"
