# TaskFlow

## Запуск бэкенда

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Создать БД (PostgreSQL):
```bash
createdb taskflow
```

Запустить сервер:
```bash
uvicorn app.main:app --reload --port 8001
```

API docs: http://localhost:8001/api/docs

## Заполнение БД тестовыми данными

После запуска бэкенда можно заполнить БД демонстрационными данными:

```bash
cd backend
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate   # Linux/Mac
python seed.py
```

Скрипт создаст:
- **7 пользователей** — 1 админ, 2 менеджера, 4 сотрудника
- **3 проекта** с участниками и историей чата
- **40+ задач** с разными статусами, приоритетами и дедлайнами

| Роль | Логин | Email |
|---|---|---|
| admin | admin | admin@taskflow.ru |
| manager | ivanov | ivanov@taskflow.ru |
| manager | petrov | petrov@taskflow.ru |
| employee | sidorov | sidorov@taskflow.ru |
| employee | kozlov | kozlov@taskflow.ru |
| employee | morozov | morozov@taskflow.ru |
| employee | volkov | volkov@taskflow.ru |

Пароль у всех: `password123`

> Скрипт полностью очищает БД перед заполнением, поэтому существующие данные будут удалены.

## Запуск фронтенда (dev)

```bash
cd frontend
npm install
npm run dev
```

Откроется на http://localhost:5173

## Продакшн сборка

```bash
cd frontend
npm run build
# dist/ скопируется и FastAPI начнёт его раздавать
```

## Переменные окружения

`backend/.env`:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/taskflow
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=60
```
