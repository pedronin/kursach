# TaskFlow

## Запуск бэкенда

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# создать базу
createdb taskflow

# запустить
uvicorn app.main:app --reload --port 8001
```

API docs: http://localhost:8001/api/docs

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
