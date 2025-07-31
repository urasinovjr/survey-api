from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json
from domain.models import Version, Question, Response
from datetime import datetime
import pytz
from db.settings import Settings

settings = Settings()

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    version = Version(name="v1.0")
    db.add(version)
    db.commit()
    db.refresh(version)

    # Full list of all 200 questions from Excel
    questions = [
        # OP: 12 questions
        Question(version_id=version.id, number="1.1", text="Наименование объекта", type="dropdown", options=json.dumps({"values": ["Жилой дом", "Коммерческое здание"]}), constraints=json.dumps({"default": "Жилой дом"})),
        Question(version_id=version.id, number="1.2", text="Адрес объекта", type="text", constraints=json.dumps({"example": "г. Москва, ул. Дмитрия Ульянова, влд. 47"})),
        Question(version_id=version.id, number="1.3", text="Назначение объекта", type="text", constraints=json.dumps({"example": "Жилое здание (Ф1.3)"})),
        Question(version_id=version.id, number="1.4", text="Класс комфорта", type="dropdown", options=json.dumps({"values": ["Стандарт", "Комфорт", "Комфорт+", "Бизнес", "Премиум", "Элит"]}), constraints=json.dumps({"default": "Стандарт"})),
        Question(version_id=version.id, number="1.5", text="Период применения индексов изменения сметной стоимости (квартал и год)", type="dropdown", options=json.dumps({"values": ["1 квартал 2022", "2 квартал 2022", "3 квартал 2022", "4 квартал 2022", "1 квартал 2023", "2 квартал 2023", "3 квартал 2023", "4 квартал 2023", "1 квартал 2024", "2 квартал 2024", "3 квартал 2024", "4 квартал 2024", "1 квартал 2025", "2 квартал 2025", "3 квартал 2025", "4 квартал 2025"]}), constraints=json.dumps({"default": "3 квартал 2024"})),
        Question(version_id=version.id, number="1.6", text="Регион строительства", type="dropdown", options=json.dumps({"values": ["г.Москва", "Московская область"]}), constraints=json.dumps({"default": "г.Москва"})),
        Question(version_id=version.id, number="1.7", text="Сейсмичность региона строительства", type="dropdown", options=json.dumps({"values": ["10 баллов", "9 баллов", "8 баллов", "7 баллов", "менее 7 баллов"]}), constraints=json.dumps({"default": "менее 7 баллов"})),
        Question(version_id=version.id, number="1.8", text="Площадь участка строительства, м²", type="integer", constraints=json.dumps({"min": 1, "example": 11303})),
        Question(version_id=version.id, number="1.9", text="Площадь застройки, м²", type="integer", constraints=json.dumps({"min": 1, "example": 6032})),
        Question(version_id=version.id, number="1.10", text="Конструктивная схема объекта", type="dropdown", options=json.dumps({"values": ["монолитно-кирпичный", "монолитно-каркасный", "монолитный", "панельный", "кирпичный"]}), constraints=json.dumps({"default": "монолитно-каркасный"})),
        Question(version_id=version.id, number="1.11", text="Тип фасадного остекления", type="dropdown", options=json.dumps({"values": ["Сплошное остекление от пола", "Классическое остекление с окнами и подоконным пространством", "Смешанное - Сплошное / Классическое 50/50"]}), constraints=json.dumps({"default": "Классическое остекление с окнами и подоконным пространством"})),
        Question(version_id=version.id, number="1.12", text="Тип фундамента", type="dropdown", options=json.dumps({"values": ["Свайный фундамент", "Монолитная плита на естественном основании"]}), constraints=json.dumps({"default": "Монолитная плита на естественном основании"})),
        # ОЛ_вэб: 37 вопросов
        Question(version_id=version.id, number="2.1", text="Количество корпусов, конструктивно связанных между собой", type="integer", constraints=json.dumps({"min": 1, "max": 20, "example": 2})),
        Question(version_id=version.id, number="2.1.1", text="Выберите корпуса, которые размещаются на общей плите подземной части", type="dropdown", options=json.dumps({"values": [], "depends_on": "2.1", "condition": ">1"}), constraints=json.dumps({"dynamic_options": True, "exclude_from": ["2.2.1", "2.3.1"]})),
        Question(version_id=version.id, number="2.2", text="Количество стилобатов на объекте", type="integer", constraints=json.dumps({"min": 0, "max_ref": "2.1", "example": 0})),
        Question(version_id=version.id, number="2.2.1", text="Выберите корпус, который связан со стилобатом", type="dropdown", options=json.dumps({"values": [], "depends_on": "2.2", "condition": ">0"}), constraints=json.dumps({"dynamic_options": True, "exclude_from": ["2.1.1", "2.3.1"]})),
        Question(version_id=version.id, number="2.3", text="Количество пристроек с помещениями общественного назначения на объекте", type="integer", constraints=json.dumps({"min": 0, "max_ref": "2.1", "example": 1})),
        Question(version_id=version.id, number="2.3.1", text="Выберите корпус, который связан с пристройкой", type="dropdown", options=json.dumps({"values": [], "depends_on": "2.3", "condition": ">0"}), constraints=json.dumps({"dynamic_options": True, "exclude_from": ["2.1.1", "2.2.1"]})),
        Question(version_id=version.id, number="2.1.2", text="Количество этажей в корпусе", type="integer", constraints=json.dumps({"min": 1, "max": 100, "example": 17, "prefill_from_previous": True})),
        Question(version_id=version.id, number="2.1.3", text="Количество секций в корпусе", type="integer", constraints=json.dumps({"min": 1, "example": 2, "prefill_from_previous": True})),
        Question(version_id=version.id, number="2.1.4", text="Общая площадь квартир в корпусе, м²", type="integer", constraints=json.dumps({"min": 100, "max": 200000, "example": 5000})),
        Question(version_id=version.id, number="2.1.5", text="Общая площадь нежилых помещений в корпусе, м²", type="integer", constraints=json.dumps({"min": 0, "max": 100000, "example": 1000})),
        Question(version_id=version.id, number="2.1.6", text="Общая площадь квартир объекта (с учетом летних помещений), м²", type="integer", constraints=json.dumps({"min": 100, "max": 200000, "max_ref_percent": {"ref": "2.1.4", "percent": 80}, "example": 4000})),
        Question(version_id=version.id, number="2.1.7", text="Общая площадь встроенных помещений общественного назначения, м²", type="integer", constraints=json.dumps({"min": 0, "max": 50000, "example": 500})),
        Question(version_id=version.id, number="2.1.8", text="Общая площадь помещений общественного назначения в стилобате, м²", type="integer", constraints=json.dumps({"min": 0, "max": 50000, "example": 0, "depends_on": "2.2", "condition": ">0"})),
        Question(version_id=version.id, number="2.1.9", text="Количество машиномест в подземной автостоянке", type="integer", constraints=json.dumps({"min": 0, "example": 50})),
        Question(version_id=version.id, number="2.1.10", text="Площадь подземной части, м²", type="integer", constraints=json.dumps({"min": 0, "example": 3000})),
        Question(version_id=version.id, number="2.1.11", text="Количество подземных этажей", type="integer", constraints=json.dumps({"min": 0, "max": 5, "example": 1})),
        Question(version_id=version.id, number="2.1.12", text="Высота подземной части, м", type="integer", constraints=json.dumps({"min": 0, "example": 3})),
        Question(version_id=version.id, number="2.1.13", text="Пожарно-техническая высота секции корпуса, м", type="integer", constraints=json.dumps({"min": 1, "example": 50, "depends_on_stilobate": "2.2"})),
        Question(version_id=version.id, number="2.1.14", text="Общая площадь технических помещений, м²", type="integer", constraints=json.dumps({"min": 0, "example": 200})),
        Question(version_id=version.id, number="2.1.15", text="Площадь кровли, м²", type="integer", constraints=json.dumps({"min": 0, "example": 1000})),
        Question(version_id=version.id, number="2.1.16", text="Тип кровли", type="dropdown", options=json.dumps({"values": ["Плоская", "Скатная", "Эксплуатируемая"]}), constraints=json.dumps({"default": "Плоская"})),
        Question(version_id=version.id, number="2.1.17", text="Наличие технического этажа", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="2.1.18", text="Наличие чердака", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="2.1.19", text="Наличие мансарды", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="2.1.20", text="Тип наружных стен", type="dropdown", options=json.dumps({"values": ["Кирпич", "Монолит", "Панели"]}), constraints=json.dumps({"default": "Кирпич"})),
        Question(version_id=version.id, number="2.1.21", text="Тип перекрытий", type="dropdown", options=json.dumps({"values": ["Монолитные", "Сборные", "Смешанные"]}), constraints=json.dumps({"default": "Монолитные"})),
        Question(version_id=version.id, number="2.1.22", text="Количество лифтов в корпусе", type="integer", constraints=json.dumps({"min": 0, "example": 2, "depends_on": ["2.1.2", "2.1.4"]})),
        Question(version_id=version.id, number="2.1.23", text="Наличие мусоропровода", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="2.1.24", text="Наличие системы дымоудаления", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="2.1.25", text="Тип системы отопления", type="dropdown", options=json.dumps({"values": ["Центральное", "Индивидуальное", "Комбинированное"]}), constraints=json.dumps({"default": "Центральное"})),
        Question(version_id=version.id, number="2.1.26", text="Тип системы вентиляции", type="dropdown", options=json.dumps({"values": ["Естественная", "Принудительная", "Комбинированная"]}), constraints=json.dumps({"default": "Естественная"})),
        Question(version_id=version.id, number="2.1.27", text="Тип системы водоснабжения", type="dropdown", options=json.dumps({"values": ["Центральное", "Автономное"]}), constraints=json.dumps({"default": "Центральное"})),
        Question(version_id=version.id, number="2.1.28", text="Тип системы канализации", type="dropdown", options=json.dumps({"values": ["Центральная", "Автономная"]}), constraints=json.dumps({"default": "Центральная"})),
        Question(version_id=version.id, number="2.1.29", text="Наличие системы кондиционирования", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="3.5.рд.св.кор", text="Количество пожарных отсеков надземной части объекта", type="integer", constraints=json.dumps({"min": 1, "example": 1, "editable": True})),
        Question(version_id=version.id, number="3.6.рд.св.кор", text="Степень огнестойкости пожарного отсека", type="text", constraints=json.dumps({"read_only": True, "calculation": "II if 2.1.13 < 50 else I", "example": "I"})),
        Question(version_id=version.id, number="3.7.рд.св.кор", text="Класс конструктивной пожарной опасности отсека", type="text", constraints=json.dumps({"read_only": True, "example": "C0"})),
        Question(version_id=version.id, number="3.8.рд.св.кор", text="Предел огнестойкости основных строительных конструкций", type="text", constraints=json.dumps({"read_only": True, "calculation": {"<50": "R90", "50-75": "R120", "75-100": "R150", "100-150": "R180", ">150": "R240"}, "example": "R120"})),
        # ОЛ_заполнение: 29 questions
        Question(version_id=version.id, number="4.1", text="Наличие системы видеонаблюдения", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.2", text="Наличие системы контроля доступа", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.3", text="Наличие системы пожарной сигнализации", type="boolean", constraints=json.dumps({"default": True, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.4", text="Расчетный коэффициент для наружных инженерных сетей (ИС), в т.ч. затраты на техприсоединение к ИС", type="integer", constraints=json.dumps({"min": 10000000, "max": 400000000, "example": 10000})),
        Question(version_id=version.id, number="4.5", text="Расчетный коэффициент для благоустройства и озеленения территории", type="integer", constraints=json.dumps({"min": 20000000, "max": 90000000, "example": 1000})),
        Question(version_id=version.id, number="4.6", text="Площадь озеленения, м²", type="integer", constraints=json.dumps({"min": 0, "example": 500})),
        Question(version_id=version.id, number="4.7", text="Количество детских площадок", type="integer", constraints=json.dumps({"min": 0, "example": 1})),
        Question(version_id=version.id, number="4.8", text="Количество спортивных площадок", type="integer", constraints=json.dumps({"min": 0, "example": 1})),
        Question(version_id=version.id, number="4.9", text="Наличие парковочных мест на территории", type="integer", constraints=json.dumps({"min": 0, "example": 20})),
        Question(version_id=version.id, number="4.10", text="Тип покрытия дорог на территории", type="dropdown", options=json.dumps({"values": ["Асфальт", "Бетон", "Плитка"]}), constraints=json.dumps({"default": "Асфальт"})),
        Question(version_id=version.id, number="4.11", text="Наличие системы освещения территории", type="boolean", constraints=json.dumps({"default": True, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.12", text="Тип системы освещения", type="dropdown", options=json.dumps({"values": ["Светодиодное", "Галогенное", "Комбинированное"]}), constraints=json.dumps({"default": "Светодиодное", "depends_on": "4.11", "condition": "True"})),
        Question(version_id=version.id, number="4.13", text="Наличие системы полива газонов", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.14", text="Количество деревьев на территории", type="integer", constraints=json.dumps({"min": 0, "example": 50})),
        Question(version_id=version.id, number="4.15", text="Количество кустарников на территории", type="integer", constraints=json.dumps({"min": 0, "example": 100})),
        Question(version_id=version.id, number="4.16", text="Наличие велодорожек", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.17", text="Площадь велодорожек, м²", type="integer", constraints=json.dumps({"min": 0, "example": 200, "depends_on": "4.16", "condition": "True"})),
        Question(version_id=version.id, number="4.18", text="Наличие системы ливневой канализации", type="boolean", constraints=json.dumps({"default": True, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.19", text="Тип системы ливневой канализации", type="dropdown", options=json.dumps({"values": ["Открытая", "Закрытая", "Комбинированная"]}), constraints=json.dumps({"default": "Закрытая", "depends_on": "4.18", "condition": "True"})),
        Question(version_id=version.id, number="4.20", text="Наличие системы утилизации отходов", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.21", text="Тип системы утилизации отходов", type="dropdown", options=json.dumps({"values": ["Контейнеры", "Подземные баки", "Комбинированная"]}), constraints=json.dumps({"default": "Контейнеры", "depends_on": "4.20", "condition": "True"})),
        Question(version_id=version.id, number="4.22", text="Наличие системы шумозащиты", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.23", text="Тип системы шумозащиты", type="dropdown", options=json.dumps({"values": ["Экраны", "Зеленые насаждения", "Комбинированная"]}), constraints=json.dumps({"default": "Экраны", "depends_on": "4.22", "condition": "True"})),
        Question(version_id=version.id, number="4.24", text="Наличие системы охраны", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.25", text="Тип системы охраны", type="dropdown", options=json.dumps({"values": ["Физическая охрана", "Электронная охрана", "Комбинированная"]}), constraints=json.dumps({"default": "Электронная охрана", "depends_on": "4.24", "condition": "True"})),
        Question(version_id=version.id, number="4.26", text="Наличие системы автоматического пожаротушения", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.27", text="Тип системы пожаротушения", type="dropdown", options=json.dumps({"values": ["Водяная", "Порошковая", "Газовая"]}), constraints=json.dumps({"default": "Водяная", "depends_on": "4.26", "condition": "True"})),
        Question(version_id=version.id, number="4.28", text="Наличие системы управления зданием (BMS)", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.29", text="Тип системы BMS", type="dropdown", options=json.dumps({"values": ["Базовая", "Расширенная", "Интеграционная"]}), constraints=json.dumps({"default": "Базовая", "depends_on": "4.28", "condition": "True"})),
        # ОЛ_29+8+72: 109 questions
        Question(version_id=version.id, number="4.30", text="Наличие системы 'Умный дом'", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.31", text="Тип системы 'Умный дом'", type="dropdown", options=json.dumps({"values": ["Базовая", "Расширенная", "Полная интеграция"]}), constraints=json.dumps({"default": "Базовая", "depends_on": "4.30", "condition": "True"})),
        Question(version_id=version.id, number="4.32", text="Наличие системы электрочасофикации (ЭЧ)", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.33", text="Тип системы ЭЧ", type="dropdown", options=json.dumps({"values": ["Аналоговая", "Цифровая"]}), constraints=json.dumps({"default": "Цифровая", "depends_on": "4.32", "condition": "True"})),
        Question(version_id=version.id, number="4.34", text="Площадь коммерческих помещений, м²", type="integer", constraints=json.dumps({"min": 0, "example": 1000})),
        Question(version_id=version.id, number="4.35", text="Количество коммерческих помещений", type="integer", constraints=json.dumps({"min": 0, "example": 5})),
        Question(version_id=version.id, number="4.36", text="Наличие встроенных парковок", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.37", text="Количество встроенных парковочных мест", type="integer", constraints=json.dumps({"min": 0, "example": 10, "depends_on": "4.36", "condition": "True"})),
        Question(version_id=version.id, number="4.38", text="Наличие отдельно стоящих гаражей", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.39", text="Количество мест в отдельно стоящих гаражах", type="integer", constraints=json.dumps({"min": 0, "example": 20, "depends_on": "4.38", "condition": "True"})),
        Question(version_id=version.id, number="4.40", text="Площадь тротуаров, м²", type="integer", constraints=json.dumps({"min": 0, "example": 500})),
        Question(version_id=version.id, number="4.41", text="Тип покрытия тротуаров", type="dropdown", options=json.dumps({"values": ["Асфальт", "Плитка", "Бетон"]}), constraints=json.dumps({"default": "Плитка"})),
        Question(version_id=version.id, number="4.42", text="Наличие системы обогрева тротуаров", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.43", text="Площадь зон отдыха, м²", type="integer", constraints=json.dumps({"min": 0, "example": 300})),
        Question(version_id=version.id, number="4.44", text="Наличие фонтанов", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.45", text="Количество фонтанов", type="integer", constraints=json.dumps({"min": 0, "example": 1, "depends_on": "4.44", "condition": "True"})),
        Question(version_id=version.id, number="4.46", text="Наличие системы видеодомофонов", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.47", text="Тип видеодомофонов", type="dropdown", options=json.dumps({"values": ["Аналоговые", "Цифровые", "IP"]}), constraints=json.dumps({"default": "IP", "depends_on": "4.46", "condition": "True"})),
        Question(version_id=version.id, number="4.48", text="Наличие системы контроля загазованности", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.49", text="Тип системы контроля загазованности", type="dropdown", options=json.dumps({"values": ["Автономная", "Интегрированная"]}), constraints=json.dumps({"default": "Автономная", "depends_on": "4.48", "condition": "True"})),
        Question(version_id=version.id, number="4.50", text="Наличие системы системы молниезащиты", type="boolean", constraints=json.dumps({"default": True, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.51", text="Тип системы молниезащиты", type="dropdown", options=json.dumps({"values": ["Активная", "Пассивная"]}), constraints=json.dumps({"default": "Пассивная", "depends_on": "4.50", "condition": "True"})),
        Question(version_id=version.id, number="4.52", text="Наличие системы заземления", type="boolean", constraints=json.dumps({"default": True, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.53", text="Тип системы заземления", type="dropdown", options=json.dumps({"values": ["TN-C", "TN-S", "TN-C-S"]}), constraints=json.dumps({"default": "TN-S", "depends_on": "4.52", "condition": "True"})),
        Question(version_id=version.id, number="4.54", text="Количество трансформаторных подстанций", type="integer", constraints=json.dumps({"min": 0, "example": 1})),
        Question(version_id=version.id, number="4.55", text="Мощность трансформаторных подстанций, кВт", type="integer", constraints=json.dumps({"min": 0, "example": 1000})),
        Question(version_id=version.id, number="4.56", text="Наличие резервного электроснабжения", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.57", text="Тип резервного электроснабжения", type="dropdown", options=json.dumps({"values": ["Генератор", "ИБП", "Комбинированное"]}), constraints=json.dumps({"default": "Генератор", "depends_on": "4.56", "condition": "True"})),
        Question(version_id=version.id, number="4.58", text="Площадь помещений для инженерного оборудования, м²", type="integer", constraints=json.dumps({"min": 0, "example": 200})),
        Question(version_id=version.id, number="4.59", text="Наличие системы водоочистки", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.60", text="Тип системы водоочистки", type="dropdown", options=json.dumps({"values": ["Механическая", "Химическая", "Комбинированная"]}), constraints=json.dumps({"default": "Механическая", "depends_on": "4.59", "condition": "True"})),
        Question(version_id=version.id, number="4.61", text="Наличие системы теплоснабжения", type="boolean", constraints=json.dumps({"default": True, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.62", text="Тип системы теплоснабжения", type="dropdown", options=json.dumps({"values": ["Центральное", "Автономное", "Комбинированное"]}), constraints=json.dumps({"default": "Центральное", "depends_on": "4.61", "condition": "True"})),
        Question(version_id=version.id, number="4.63", text="Количество тепловых пунктов", type="integer", constraints=json.dumps({"min": 0, "example": 1})),
        Question(version_id=version.id, number="4.64", text="Мощность тепловых пунктов, кВт", type="integer", constraints=json.dumps({"min": 0, "example": 500})),
        Question(version_id=version.id, number="4.65", text="Наличие системы холодоснабжения", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.66", text="Тип системы холодоснабжения", type="dropdown", options=json.dumps({"values": ["Центральное", "Автономное"]}), constraints=json.dumps({"default": "Центральное", "depends_on": "4.65", "condition": "True"})),
        Question(version_id=version.id, number="4.67", text="Количество холодильных установок", type="integer", constraints=json.dumps({"min": 0, "example": 1})),
        Question(version_id=version.id, number="4.68", text="Мощность холодильных установок, кВт", type="integer", constraints=json.dumps({"min": 0, "example": 200})),
        Question(version_id=version.id, number="4.69", text="Наличие системы газоснабжения", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.70", text="Тип системы газоснабжения", type="dropdown", options=json.dumps({"values": ["Центральное", "Автономное"]}), constraints=json.dumps({"default": "Центральное", "depends_on": "4.69", "condition": "True"})),
        Question(version_id=version.id, number="4.71", text="Количество газовых котлов", type="integer", constraints=json.dumps({"min": 0, "example": 0, "depends_on": "4.69", "condition": "True"})),
        Question(version_id=version.id, number="4.72", text="Мощность газовых котлов, кВт", type="integer", constraints=json.dumps({"min": 0, "example": 0, "depends_on": "4.69", "condition": "True"})),
        Question(version_id=version.id, number="4.73", text="Наличие системы умного освещения", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.74", text="Тип системы умного освещения", type="dropdown", options=json.dumps({"values": ["Датчики движения", "Таймеры", "Комбинированная"]}), constraints=json.dumps({"default": "Датчики движения", "depends_on": "4.73", "condition": "True"})),
        Question(version_id=version.id, number="4.75", text="Наличие системы управления лифтами", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.76", text="Тип системы управления лифтами", type="dropdown", options=json.dumps({"values": ["Стандартная", "Интеллектуальная"]}), constraints=json.dumps({"default": "Стандартная", "depends_on": "4.75", "condition": "True"})),
        Question(version_id=version.id, number="4.77", text="Наличие системы мониторинга инженерных систем", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.78", text="Тип системы мониторинга", type="dropdown", options=json.dumps({"values": ["Локальная", "Облачная"]}), constraints=json.dumps({"default": "Локальная", "depends_on": "4.77", "condition": "True"})),
        Question(version_id=version.id, number="4.79", text="Наличие системы управления парковкой", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.80", text="Тип системы управления парковкой", type="dropdown", options=json.dumps({"values": ["Автоматическая", "Полуавтоматическая"]}), constraints=json.dumps({"default": "Автоматическая", "depends_on": "4.79", "condition": "True"})),
        Question(version_id=version.id, number="4.81", text="Наличие системы солнечных панелей", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.82", text="Мощность солнечных панелей, кВт", type="integer", constraints=json.dumps({"min": 0, "example": 0, "depends_on": "4.81", "condition": "True"})),
        Question(version_id=version.id, number="4.83", text="Наличие системы сбора дождевой воды", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.84", text="Объем системы сбора дождевой воды, м³", type="integer", constraints=json.dumps({"min": 0, "example": 0, "depends_on": "4.83", "condition": "True"})),
        Question(version_id=version.id, number="4.85", text="Наличие системы рекуперации тепла", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.86", text="Тип системы рекуперации тепла", type="dropdown", options=json.dumps({"values": ["Пластинчатая", "Роторная"]}), constraints=json.dumps({"default": "Пластинчатая", "depends_on": "4.85", "condition": "True"})),
        Question(version_id=version.id, number="4.87", text="Наличие системы управления шторами", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.88", text="Тип системы управления шторами", type="dropdown", options=json.dumps({"values": ["Автоматическая", "Ручная"]}), constraints=json.dumps({"default": "Автоматическая", "depends_on": "4.87", "condition": "True"})),
        Question(version_id=version.id, number="4.89", text="Наличие системы умного учета ресурсов", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.90", text="Тип системы умного учета", type="dropdown", options=json.dumps({"values": ["Вода", "Электричество", "Комбинированная"]}), constraints=json.dumps({"default": "Комбинированная", "depends_on": "4.89", "condition": "True"})),
        Question(version_id=version.id, number="4.91", text="Наличие системы управления климатом", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.92", text="Тип системы управления климатом", type="dropdown", options=json.dumps({"values": ["Локальная", "Централизованная"]}), constraints=json.dumps({"default": "Локальная", "depends_on": "4.91", "condition": "True"})),
        Question(version_id=version.id, number="4.93", text="Наличие системы управления освещением", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.94", text="Тип системы управления освещением", type="dropdown", options=json.dumps({"values": ["Датчики", "Таймеры", "Комбинированная"]}), constraints=json.dumps({"default": "Датчики", "depends_on": "4.93", "condition": "True"})),
        Question(version_id=version.id, number="4.95", text="Наличие системы управления доступом", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.96", text="Тип системы управления доступом", type="dropdown", options=json.dumps({"values": ["Кодовые замки", "Карт-ридеры", "Биометрия"]}), constraints=json.dumps({"default": "Карт-ридеры", "depends_on": "4.95", "condition": "True"})),
        Question(version_id=version.id, number="4.97", text="Наличие системы умного паркинга", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.98", text="Тип системы умного паркинга", type="dropdown", options=json.dumps({"values": ["Автоматическая", "Полуавтоматическая"]}), constraints=json.dumps({"default": "Автоматическая", "depends_on": "4.97", "condition": "True"})),
        Question(version_id=version.id, number="4.99", text="Наличие системы умного дома для коммерческих помещений", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.100", text="Тип системы умного дома для коммерческих помещений", type="dropdown", options=json.dumps({"values": ["Базовая", "Расширенная"]}), constraints=json.dumps({"default": "Базовая", "depends_on": "4.99", "condition": "True"})),
        Question(version_id=version.id, number="4.101", text="Наличие системы управления вентиляцией", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.102", text="Тип системы управления вентиляцией", type="dropdown", options=json.dumps({"values": ["Автоматическая", "Ручная"]}), constraints=json.dumps({"default": "Автоматическая", "depends_on": "4.101", "condition": "True"})),
        Question(version_id=version.id, number="4.103", text="Наличие системы умной уборки", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.104", text="Тип системы умной уборки", type="dropdown", options=json.dumps({"values": ["Роботы", "Автоматизированная"]}), constraints=json.dumps({"default": "Роботы", "depends_on": "4.103", "condition": "True"})),
        Question(version_id=version.id, number="4.105", text="Наличие системы управления энергоэффективностью", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.106", text="Тип системы энергоэффективности", type="dropdown", options=json.dumps({"values": ["Пассивная", "Активная"]}), constraints=json.dumps({"default": "Пассивная", "depends_on": "4.105", "condition": "True"})),
        Question(version_id=version.id, number="4.107", text="Наличие системы умного управления водой", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        Question(version_id=version.id, number="4.108", text="Тип системы умного управления водой", type="dropdown", options=json.dumps({"values": ["Датчики", "Автоматизированная"]}), constraints=json.dumps({"default": "Датчики", "depends_on": "4.107", "condition": "True"})),
        Question(version_id=version.id, number="4.109", text="Наличие системы управления безопасностью", type="boolean", constraints=json.dumps({"default": False, "input_type": "radiobutton"})),
        # Передача: 8 questions
        Question(version_id=version.id, number="5.1", text="Общая площадь объекта, м²", type="integer", constraints=json.dumps({"min": 100, "example": 10000})),
        Question(version_id=version.id, number="5.2", text="Общая площадь жилых помещений, м²", type="integer", constraints=json.dumps({"min": 100, "example": 8000})),
        Question(version_id=version.id, number="5.3", text="Общая площадь коммерческих помещений, м²", type="integer", constraints=json.dumps({"min": 0, "example": 2000})),
        Question(version_id=version.id, number="5.4", text="Общее количество квартир", type="integer", constraints=json.dumps({"min": 0, "example": 100})),
        Question(version_id=version.id, number="5.5", text="Общее количество машиномест", type="integer", constraints=json.dumps({"min": 0, "example": 50})),
        Question(version_id=version.id, number="5.6", text="Общая площадь благоустройства, м²", type="integer", constraints=json.dumps({"min": 0, "example": 5000})),
        Question(version_id=version.id, number="5.7", text="Количество корпусов (итоговое)", type="integer", constraints=json.dumps({"min": 1, "max": 20, "example": 2})),
        Question(version_id=version.id, number="5.8", text="Общая строительная площадь, м²", type="integer", constraints=json.dumps({"min": 100, "example": 12000})),
        # Проверка количества квартир: 5 questions
        Question(version_id=version.id, number="6.1", text="Количество 1-комнатных квартир", type="integer", constraints=json.dumps({"min": 0, "example": 10, "area_check": {"min_area": 20, "max_area": 80}})),
        Question(version_id=version.id, number="6.2", text="Количество 2-комнатных квартир", type="integer", constraints=json.dumps({"min": 0, "example": 10, "area_check": {"min_area": 35, "max_area": 120}})),
        Question(version_id=version.id, number="6.3", text="Количество 3-комнатных квартир", type="integer", constraints=json.dumps({"min": 0, "example": 10, "area_check": {"min_area": 50, "max_area": 200}})),
        Question(version_id=version.id, number="6.4", text="Количество 4-комнатных квартир", type="integer", constraints=json.dumps({"min": 0, "example": 0, "area_check": {"min_area": 65, "max_area": 250}})),
        Question(version_id=version.id, number="6.5", text="Количество квартир более 4 комнат", type="integer", constraints=json.dumps({"min": 0, "example": 0, "area_check": {"min_area": 80, "max_area": 300}})),
    ]
    db.add_all(questions)
    db.commit()
    db.close()