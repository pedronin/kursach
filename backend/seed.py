"""
Заполняет БД тестовыми данными.
Запуск: python seed.py
Все пароли: password123
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timedelta
import random
from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.models.project_member import ProjectMember
from app.models.project_comment import ProjectComment
from app.utils.security import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# очищаем в правильном порядке (зависимости)
from app.models.invite import Invite
db.query(ProjectComment).delete()
db.query(Task).delete()
db.query(ProjectMember).delete()
db.query(Invite).delete()
db.query(Project).delete()
db.query(User).delete()
db.commit()

# --- Пользователи ---
users_data = [
    ("admin",    "admin@taskflow.ru",    "admin"),
    ("ivanov",   "ivanov@taskflow.ru",   "manager"),
    ("petrov",   "petrov@taskflow.ru",   "manager"),
    ("sidorov",  "sidorov@taskflow.ru",  "employee"),
    ("kozlov",   "kozlov@taskflow.ru",   "employee"),
    ("morozov",  "morozov@taskflow.ru",  "employee"),
    ("volkov",   "volkov@taskflow.ru",   "employee"),
]

users = {}
for username, email, role in users_data:
    u = User(username=username, email=email, password_hash=hash_password("password123"), role=role)
    db.add(u)
    db.flush()
    users[username] = u

db.commit()

# --- Проекты ---
now = datetime.utcnow()

projects_data = [
    ("Редизайн сайта",       "Полный редизайн корпоративного сайта",         "ivanov"),
    ("Мобильное приложение", "Разработка мобильного приложения для клиентов", "ivanov"),
    ("Внутренний портал",    "Система документооборота для сотрудников",      "petrov"),
]

projects = {}
for title, desc, owner in projects_data:
    p = Project(
        title=title,
        description=desc,
        owner_id=users[owner].id,
        created_at=now - timedelta(days=random.randint(20, 60)),
    )
    db.add(p)
    db.flush()
    projects[title] = p

db.commit()

# --- Участники проектов ---
memberships = [
    ("Редизайн сайта",       ["sidorov", "kozlov", "morozov"]),
    ("Мобильное приложение", ["kozlov", "volkov"]),
    ("Внутренний портал",    ["sidorov", "morozov", "volkov"]),
]

for proj_title, member_names in memberships:
    proj = projects[proj_title]
    for name in member_names:
        db.add(ProjectMember(project_id=proj.id, user_id=users[name].id))

db.commit()

# --- Задачи ---
statuses = ["todo", "in_progress", "done"]
priorities = ["high", "medium", "low"]

tasks_data = [
    # Редизайн сайта
    ("Анализ конкурентов",        "Изучить топ-10 конкурентов и составить отчёт",       "Редизайн сайта", "done",        "medium", "sidorov",  -20, -5),
    ("Разработка макетов",        "Figma-макеты главной и внутренних страниц",           "Редизайн сайта", "done",        "high",   "kozlov",   -15, -3),
    ("Вёрстка главной страницы",  "HTML/CSS по утверждённым макетам",                    "Редизайн сайта", "in_progress", "high",   "sidorov",  -10,  5),
    ("Вёрстка страницы услуг",    "Адаптивная вёрстка раздела услуг",                   "Редизайн сайта", "in_progress", "medium", "kozlov",   -7,   3),
    ("Интеграция CMS",            "Подключить WordPress к новому шаблону",               "Редизайн сайта", "todo",        "medium", "morozov",  -3,   7),
    ("SEO-оптимизация",           "Мета-теги, sitemap, robots.txt",                     "Редизайн сайта", "todo",        "low",    "morozov",  -2,  14),
    ("Тестирование на устройствах","Кроссбраузерное тестирование",                       "Редизайн сайта", "todo",        "high",   "sidorov",  -1,   2),
    ("Деплой на прод",            "Переезд на боевой сервер",                           "Редизайн сайта", "todo",        "high",   "kozlov",    0,   1),

    # Мобильное приложение
    ("Проектирование архитектуры","Выбор стека, ER-диаграмма, API-контракт",            "Мобильное приложение", "done",        "high",   "kozlov",   -25, -10),
    ("Дизайн UX/UI",              "Прототип в Figma для iOS и Android",                  "Мобильное приложение", "done",        "high",   "volkov",   -18,  -6),
    ("Экран авторизации",         "Логин, регистрация, восстановление пароля",           "Мобильное приложение", "done",        "medium", "kozlov",   -12,  -2),
    ("Каталог товаров",           "Список, фильтры, карточка товара",                    "Мобильное приложение", "in_progress", "high",   "volkov",   -8,   4),
    ("Корзина и оформление",      "Добавление в корзину, оформление заказа",             "Мобильное приложение", "in_progress", "high",   "kozlov",   -5,   3),
    ("Push-уведомления",          "Firebase интеграция",                                 "Мобильное приложение", "todo",        "medium", "volkov",   -2,   6),
    ("Тесты и QA",                "Юнит-тесты, интеграционные тесты",                   "Мобильное приложение", "todo",        "medium", "kozlov",    0,   8),

    # Внутренний портал
    ("Требования и ТЗ",           "Сбор требований от всех отделов",                    "Внутренний портал", "done",        "high",   "sidorov",  -30, -15),
    ("БД и схема данных",         "Проектирование схемы PostgreSQL",                    "Внутренний портал", "done",        "high",   "morozov",  -20,  -8),
    ("API документов",            "CRUD-эндпоинты для документов",                      "Внутренний портал", "done",        "medium", "volkov",   -14,  -4),
    ("Личный кабинет сотрудника", "Профиль, настройки, история действий",               "Внутренний портал", "in_progress", "medium", "sidorov",  -8,   5),
    ("Модуль согласования",       "Цепочки согласования документов",                    "Внутренний портал", "in_progress", "high",   "morozov",  -6,   2),
    ("Поиск по документам",       "Полнотекстовый поиск",                               "Внутренний портал", "todo",        "medium", "volkov",   -3,   4),
    ("Роли и права доступа",      "Разграничение прав по отделам",                      "Внутренний портал", "todo",        "high",   "sidorov",  -1,   1),
    ("Экспорт в PDF",             "Генерация PDF из шаблонов документов",               "Внутренний портал", "todo",        "low",    "morozov",   0,  10),
]

for title, desc, proj_title, status, priority, assignee, created_offset, deadline_offset in tasks_data:
    created = now + timedelta(days=created_offset) + timedelta(hours=random.randint(0, 8))
    deadline = now + timedelta(days=deadline_offset)
    db.add(Task(
        title=title,
        description=desc,
        status=status,
        priority=priority,
        project_id=projects[proj_title].id,
        assignee_id=users[assignee].id,
        created_at=created,
        deadline=deadline,
    ))

db.commit()

# --- Комментарии в чате проекта ---
comments_data = [
    ("Редизайн сайта", "ivanov",  "Стартуем! Прошу всех держать дедлайны.",    -18),
    ("Редизайн сайта", "sidorov", "Анализ конкурентов завершён, скидываю отчёт.", -17),
    ("Редизайн сайта", "kozlov",  "Макеты согласованы с клиентом.",             -10),
    ("Редизайн сайта", "morozov", "Начинаю интеграцию CMS на этой неделе.",     -2),

    ("Мобильное приложение", "ivanov",  "Архитектура утверждена, погнали.",     -22),
    ("Мобильное приложение", "volkov",  "Дизайн готов, сдаю в разработку.",     -14),
    ("Мобильное приложение", "kozlov",  "Экран авторизации принят на ревью.",   -10),

    ("Внутренний портал", "petrov",  "ТЗ согласовано со всеми отделами.",       -28),
    ("Внутренний портал", "morozov", "Схема БД утверждена.",                    -18),
    ("Внутренний портал", "sidorov", "API документов готово к тестированию.",   -12),
    ("Внутренний портал", "petrov",  "Напоминаю: дедлайн по модулю согласования через 2 дня!", -1),
]

for proj_title, author, text, day_offset in comments_data:
    db.add(ProjectComment(
        project_id=projects[proj_title].id,
        author_id=users[author].id,
        text=text,
        created_at=now + timedelta(days=day_offset),
    ))

db.commit()
db.close()

print("✓ База данных заполнена")
print()
print("Пользователи (пароль у всех: password123):")
for username, email, role in users_data:
    print(f"  {role:10} | {username:12} | {email}")
