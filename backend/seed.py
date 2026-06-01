"""
Заполняет БД демонстрационными данными для аналитики.
Запуск: python seed.py
Все пароли: password123

Проекты и их профили:
  Редизайн сайта       — умеренный риск (~40), смешанная нагрузка команды
  Мобильное приложение — высокий риск (~65), перегрузка ключевых сотрудников
  Внутренний портал    — низкий риск (~7),  большинство задач закрыто
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timedelta
from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.models.project_member import ProjectMember
from app.models.project_comment import ProjectComment
from app.models.invite import Invite
from app.utils.security import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# очистка
db.query(ProjectComment).delete()
db.query(Task).delete()
db.query(ProjectMember).delete()
db.query(Invite).delete()
db.query(Project).delete()
db.query(User).delete()
db.commit()

now = datetime.utcnow()
def ago(days=0, hours=0):   return now - timedelta(days=days, hours=hours)
def ahead(days=0, hours=0): return now + timedelta(days=days, hours=hours)

# ── Пользователи ──────────────────────────────────────────────────────────────
raw_users = [
    ("admin",   "admin@taskflow.ru",   "admin"),
    ("ivanov",  "ivanov@taskflow.ru",  "manager"),
    ("petrov",  "petrov@taskflow.ru",  "manager"),
    ("sidorov", "sidorov@taskflow.ru", "employee"),
    ("kozlov",  "kozlov@taskflow.ru",  "employee"),
    ("morozov", "morozov@taskflow.ru", "employee"),
    ("volkov",  "volkov@taskflow.ru",  "employee"),
]
users = {}
for username, email, role in raw_users:
    u = User(username=username, email=email,
             password_hash=hash_password("password123"), role=role)
    db.add(u); db.flush()
    users[username] = u
db.commit()

# ── Проекты ───────────────────────────────────────────────────────────────────
def add_project(title, desc, owner, days_ago):
    p = Project(title=title, description=desc,
                owner_id=users[owner].id, created_at=ago(days_ago))
    db.add(p); db.flush()
    return p

p1 = add_project("Редизайн сайта",
                 "Полный редизайн корпоративного сайта компании", "ivanov", 45)
p2 = add_project("Мобильное приложение",
                 "Разработка мобильного приложения для клиентов", "ivanov", 30)
p3 = add_project("Внутренний портал",
                 "Система документооборота для сотрудников",      "petrov", 60)
db.commit()

# ── Участники ─────────────────────────────────────────────────────────────────
for proj, names in [
    (p1, ["sidorov", "kozlov", "morozov"]),
    (p2, ["kozlov", "volkov"]),
    (p3, ["sidorov", "morozov", "volkov"]),
]:
    for n in names:
        db.add(ProjectMember(project_id=proj.id, user_id=users[n].id))
db.commit()

# ── Задачи ────────────────────────────────────────────────────────────────────
def task(title, desc, proj, status, priority, assignee, created, deadline):
    db.add(Task(
        title=title, description=desc,
        project_id=proj.id, status=status, priority=priority,
        assignee_id=users[assignee].id,
        created_at=created, deadline=deadline,
    ))

# ═══════════════════════════════════════════════════════════════════════════════
# ПРОЕКТ 1: Редизайн сайта  — целевой Risk Index ≈ 41 (умеренный)
# Команда: sidorov (перегружен, idx≈13), kozlov (умеренно, idx≈8), morozov (свободен, idx=3)
# ═══════════════════════════════════════════════════════════════════════════════

# sidorov — workload_index = 3+3+3+2+2 = 13 → ПЕРЕГРУЖЕН
task("Разработка системы дизайна",    "Цветовая палитра, типографика, компоненты",     p1, "in_progress", "high",   "sidorov", ago(28), ago(2))   # просрочена
task("Вёрстка главной страницы",      "Адаптивная вёрстка по макетам",                 p1, "in_progress", "high",   "sidorov", ago(18), ago(1))   # просрочена
task("Вёрстка страницы услуг",        "Раздел услуг с анимациями",                     p1, "todo",        "high",   "sidorov", ago(10), ahead(2)) # срочно (2 дня)
task("Оптимизация изображений",       "WebP, lazy-load, размеры",                      p1, "in_progress", "medium", "sidorov", ago(8),  ahead(5))
task("Кроссбраузерное тестирование",  "Chrome, Firefox, Safari, Edge",                 p1, "todo",        "medium", "sidorov", ago(3),  ahead(6))
task("Аудит старого сайта",           "Анализ текущего контента и структуры",          p1, "done",        "medium", "sidorov", ago(40), ago(30))
task("Согласование требований",       "Встреча с клиентом, фиксация ТЗ",              p1, "done",        "high",   "sidorov", ago(42), ago(35))

# kozlov — workload_index = 3+2+2+1 = 8 → УМЕРЕННО
task("UX-исследование",               "Интервью с пользователями, CJM",               p1, "done",        "high",   "kozlov",  ago(38), ago(28))
task("Прототипирование в Figma",      "Wireframes всех ключевых страниц",              p1, "done",        "high",   "kozlov",  ago(30), ago(20))
task("Дизайн главной страницы",       "Финальный дизайн в Figma",                     p1, "done",        "high",   "kozlov",  ago(22), ago(12))
task("Дизайн блога и статей",         "Шаблоны для контентных страниц",               p1, "in_progress", "high",   "kozlov",  ago(12), ahead(3)) # срочно (3 дня)
task("Иконки и иллюстрации",          "Кастомный набор иконок SVG",                   p1, "todo",        "medium", "kozlov",  ago(6),  ahead(8))
task("Анимации и переходы",           "Micro-animations в CSS/JS",                    p1, "todo",        "medium", "kozlov",  ago(4),  ahead(12))
task("Документация дизайн-системы",   "Storybook + описание компонентов",             p1, "todo",        "low",    "kozlov",  ago(2),  ahead(18))

# morozov — workload_index = 2+1 = 3 → СВОБОДЕН
task("Настройка CMS",                 "WordPress, плагины, права доступа",             p1, "done",        "high",   "morozov", ago(35), ago(25))
task("SEO-оптимизация",              "Мета-теги, sitemap, robots.txt, schema.org",     p1, "todo",        "medium", "morozov", ago(5),  ahead(14))
task("Настройка аналитики",          "Google Analytics 4, Яндекс.Метрика",            p1, "todo",        "low",    "morozov", ago(3),  ahead(20))

# ═══════════════════════════════════════════════════════════════════════════════
# ПРОЕКТ 2: Мобильное приложение — целевой Risk Index ≈ 64 (высокий)
# Команда: kozlov (перегружен, idx≈14), volkov (умеренно, idx≈8)
# ═══════════════════════════════════════════════════════════════════════════════

# kozlov — workload_index = 3+3+3+3+2 = 14 → ПЕРЕГРУЖЕН
task("Архитектура приложения",        "Выбор стека, паттерны, структура проекта",      p2, "done",        "high",   "kozlov",  ago(28), ago(18))
task("Экран авторизации",             "Логин, регистрация, восстановление пароля",     p2, "done",        "high",   "kozlov",  ago(22), ago(12))
task("Каталог товаров",               "Список, фильтры, поиск, карточка",             p2, "in_progress", "high",   "kozlov",  ago(14), ago(3))  # просрочена
task("Корзина и оформление заказа",   "Добавление, редактирование, checkout flow",     p2, "in_progress", "high",   "kozlov",  ago(10), ago(1))  # просрочена
task("Интеграция платёжного шлюза",   "Stripe, Apple Pay, Google Pay",                p2, "todo",        "high",   "kozlov",  ago(5),  ahead(1)) # срочно (1 день)
task("История заказов",               "Список заказов, детальная страница",            p2, "todo",        "high",   "kozlov",  ago(3),  ahead(2)) # срочно (2 дня)
task("Профиль пользователя",          "Редактирование данных, аватар, настройки",      p2, "todo",        "medium", "kozlov",  ago(2),  ahead(7))

# volkov — workload_index = 3+3+2 = 8 → УМЕРЕННО
task("UX/UI дизайн приложения",       "Макеты всех экранов iOS и Android",            p2, "done",        "high",   "volkov",  ago(26), ago(16))
task("Онбординг и туториал",          "Экраны приветствия для новых пользователей",   p2, "done",        "medium", "volkov",  ago(18), ago(8))
task("Push-уведомления",              "Firebase, сегментация, шаблоны",               p2, "in_progress", "high",   "volkov",  ago(8),  ago(2))  # просрочена
task("Экран отслеживания заказа",     "Real-time статус доставки на карте",           p2, "in_progress", "high",   "volkov",  ago(6),  ahead(2)) # срочно (2 дня)
task("Тёмная тема",                   "Dark mode, системные настройки",               p2, "todo",        "medium", "volkov",  ago(2),  ahead(9))

# ═══════════════════════════════════════════════════════════════════════════════
# ПРОЕКТ 3: Внутренний портал — целевой Risk Index ≈ 7 (низкий)
# Команда: sidorov (свободен, idx=1), morozov (свободен, idx=4), volkov (свободен, idx=0)
# ═══════════════════════════════════════════════════════════════════════════════

# sidorov — workload_index = 1 → СВОБОДЕН
task("Сбор требований и ТЗ",          "Интервью со всеми отделами компании",           p3, "done",        "high",   "sidorov", ago(58), ago(45))
task("Проектирование БД",             "ER-диаграмма, нормализация, PostgreSQL",        p3, "done",        "high",   "sidorov", ago(50), ago(38))
task("Базовая авторизация",           "JWT, роли, права доступа по отделам",           p3, "done",        "high",   "sidorov", ago(40), ago(28))
task("Личный кабинет сотрудника",     "Профиль, контакты, история действий",           p3, "done",        "medium", "sidorov", ago(28), ago(15))
task("Интеграция с AD",               "Синхронизация с Active Directory",              p3, "done",        "high",   "sidorov", ago(18), ago(8))
task("Раздел новостей компании",      "CRUD для HR, лента для сотрудников",            p3, "todo",        "low",    "sidorov", ago(3),  ahead(21))

# morozov — workload_index = 2+2 = 4 → СВОБОДЕН
task("Проектирование API",            "REST API, OpenAPI спецификация",                p3, "done",        "high",   "morozov", ago(55), ago(42))
task("CRUD документов",               "Загрузка, хранение, версионирование",           p3, "done",        "high",   "morozov", ago(45), ago(32))
task("Модуль согласования",           "Цепочки согласования, уведомления",            p3, "done",        "high",   "morozov", ago(30), ago(18))
task("Поиск по документам",           "Полнотекстовый поиск, фильтры",                p3, "done",        "medium", "morozov", ago(20), ago(8))
task("Экспорт в PDF и Excel",         "Генерация отчётов по шаблонам",                p3, "todo",        "medium", "morozov", ago(4),  ahead(14))
task("Уведомления по email",          "SMTP, шаблоны писем, очередь",                 p3, "todo",        "medium", "morozov", ago(2),  ahead(18))

# volkov — workload_index = 0 → СВОБОДЕН (всё сдал)
task("Дизайн интерфейса портала",     "Figma, дизайн-система, компоненты",            p3, "done",        "high",   "volkov",  ago(52), ago(40))
task("Вёрстка основных разделов",     "Главная, документы, профиль, поиск",           p3, "done",        "high",   "volkov",  ago(38), ago(25))
task("Мобильная адаптация",           "Адаптивность для планшетов и телефонов",       p3, "done",        "medium", "volkov",  ago(22), ago(10))
task("Нагрузочное тестирование",      "JMeter, 500 одновременных пользователей",      p3, "done",        "medium", "volkov",  ago(10), ago(3))

db.commit()

# ── Комментарии в чат проектов ────────────────────────────────────────────────
chats = [
    (p1, "ivanov",  "Коллеги, стартуем редизайн. Прошу держать дедлайны — клиент строгий.", ago(44)),
    (p1, "sidorov", "Принял в работу систему дизайна, будет готово к пятнице.",              ago(27)),
    (p1, "kozlov",  "UX-исследование завершено. Выявили 3 ключевых проблемы навигации.",    ago(25)),
    (p1, "ivanov",  "Отлично! Фиксируем и берём в работу при проектировании.",              ago(25)),
    (p1, "kozlov",  "Прототипы готовы, жду фидбек от клиента.",                            ago(18)),
    (p1, "morozov", "CMS настроена, тестовый контент залит.",                              ago(12)),
    (p1, "sidorov", "Главная сверстана на 80%. Застрял на анимациях header'а.",            ago(5)),
    (p1, "ivanov",  "Sidorov, по главной — дедлайн уже прошёл, ускоряйся!",               ago(1)),

    (p2, "ivanov",  "Стартуем мобильное приложение. Kozlov — ты тимлид разработки.",      ago(29)),
    (p2, "kozlov",  "Понял. Архитектура готова, начинаем спринт.",                         ago(27)),
    (p2, "volkov",  "Все макеты готовы, передаю в разработку.",                            ago(15)),
    (p2, "kozlov",  "Каталог и корзина в работе, но сроки горят. Нужна помощь.",          ago(4)),
    (p2, "ivanov",  "ВНИМАНИЕ: 3 задачи уже просрочены! Нужен срочный статус.",           ago(1)),
    (p2, "volkov",  "Push-уведомления тоже просрочены, извините. Закрою сегодня.",        ago(1)),

    (p3, "petrov",  "Портал в финальной стадии. Отличная работа команды!",                 ago(5)),
    (p3, "morozov", "Все основные модули сданы. Осталось email-уведомления и экспорт.",   ago(4)),
    (p3, "sidorov", "Моя часть полностью закрыта. Готов помочь остальным.",                ago(3)),
    (p3, "volkov",  "Нагрузочное тестирование пройдено: 500 RPS без деградации.",         ago(2)),
    (p3, "petrov",  "Отлично! Планируем презентацию для руководства на следующей неделе.", ago(1)),
]

for proj, author, text, created in chats:
    db.add(ProjectComment(
        project_id=proj.id,
        author_id=users[author].id,
        text=text,
        created_at=created,
    ))

db.commit()
db.close()

print("✓ База данных заполнена\n")
print("Пользователи (пароль у всех: password123):")
for username, email, role in raw_users:
    print(f"  {role:10} | {username:12} | {email}")

print("\nОжидаемые индексы риска:")
print("  Редизайн сайта       — ~41  (умеренный, оранжевый)")
print("  Мобильное приложение — ~64  (высокий, красный)")
print("  Внутренний портал    — ~7   (низкий, зелёный)")

print("\nОжидаемые индексы нагрузки:")
print("  kozlov  — ~14 в мобильном приложении  (Перегружен)")
print("  sidorov — ~13 в редизайне сайта       (Перегружен)")
print("  volkov  — ~8  в мобильном приложении  (Умеренно)")
print("  kozlov  — ~8  в редизайне сайта       (Умеренно)")
print("  morozov — ~3  в редизайне сайта       (Свободен)")
print("  sidorov — ~1  во внутреннем портале   (Свободен)")
print("  volkov  — ~0  во внутреннем портале   (Свободен)")
