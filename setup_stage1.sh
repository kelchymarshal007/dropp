#!/bin/bash

echo "Building Stage 1: Foundation..."

# 1. Root .gitignore
cat > .gitignore << 'GITIGNORE'
.env
__pycache__/
*.pyc
node_modules/
.next/
dist/
*.log
pgdata/
.DS_Store
GITIGNORE

# 2. Environment Variables
cat > .env << 'ENV'
POSTGRES_USER=dropp
POSTGRES_PASSWORD=dropp_secure_pass_123
POSTGRES_DB=dropp_db
DATABASE_URL=postgresql+asyncpg://dropp:dropp_secure_pass_123@db:5432/dropp_db
REDIS_URL=redis://redis:6379/0
NEXT_PUBLIC_API_URL=http://localhost:8000
ENV

# 3. Docker Compose (The Orchestrator)
cat > docker-compose.yml << 'YAML'
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    env_file: .env
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  api:
    build: 
      context: ./dropp-api
    env_file: .env
    ports:
      - "8000:8000"
    volumes:
      - ./dropp-api:/app
      - ./gateways.json:/app/gateways.json
    depends_on:
      - db
      - redis

  worker:
    build:
      context: ./dropp-worker
    env_file: .env
    volumes:
      - ./dropp-worker:/app
    depends_on:
      - redis

  web:
    build:
      context: ./dropp-web
    env_file: .env
    ports:
      - "3000:3000"
    volumes:
      - ./dropp-web:/app
      - /app/node_modules
      - /app/.next
    depends_on:
      - api

volumes:
  pgdata:
YAML

# 4. BIKEM Gateway Config
cat > gateways.json << 'JSON'
{
  "gateways": [
    {
      "provider": "paystack",
      "class": "RealPaystackGateway",
      "module": "app.gateways.plugins.real_paystack_gateway",
      "zone": "WEST_AFRICA",
      "priority": 1,
      "enabled": true
    }
  ]
}
JSON

# ==========================================
# 5. FASTAPI MICROSERVICE (dropp-api)
# ==========================================
cat > dropp-api/requirements.txt << 'REQ'
fastapi==0.115.0
uvicorn==0.30.6
sqlalchemy[asyncio]==2.0.35
asyncpg==0.29.0
pydantic-settings==2.5.2
redis==5.0.8
celery==5.4.0
REQ

cat > dropp-api/Dockerfile << 'DOCKER'
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
DOCKER

cat > dropp-api/app/core/config.py << 'PY'
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    
    class Config:
        env_file = ".env"

settings = Settings()
PY

cat > dropp-api/app/core/database.py << 'PY'
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
PY

cat > dropp-api/app/main.py << 'PY'
from fastapi import FastAPI
from app.core.database import engine, Base

app = FastAPI(title="Dropp Core API", version="1.0.0")

@app.on_event("startup")
async def startup():
    # In production, use Alembic. For now, create tables on startup.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database connected and tables created.")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "dropp-api"}
PY

# Create empty __init__.py files for Python modules
touch dropp-api/app/__init__.py
touch dropp-api/app/core/__init__.py
touch dropp-api/app/domain/__init__.py
touch dropp-api/app/models/__init__.py
touch dropp-api/app/schemas/__init__.py
touch dropp-api/app/api/__init__.py
touch dropp-api/app/services/__init__.py
touch dropp-api/app/gateways/__init__.py
touch dropp-api/app/gateways/plugins/__init__.py

# ==========================================
# 6. CELERY WORKER MICROSERVICE (dropp-worker)
# ==========================================
cat > dropp-worker/requirements.txt << 'REQ'
celery==5.4.0
redis==5.0.8
REQ

cat > dropp-worker/Dockerfile << 'DOCKER'
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["celery", "-A", "tasks", "worker", "--loglevel=info"]
DOCKER

cat > dropp-worker/tasks.py << 'PY'
import os
from celery import Celery

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
app = Celery('dropp_worker', broker=redis_url)

@app.task
def test_task():
    return "Worker is alive!"
PY

# ==========================================
# 7. NEXT.JS WEB MICROSERVICE (dropp-web)
# ==========================================
cat > dropp-web/Dockerfile << 'DOCKER'
FROM node:20-alpine
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
CMD ["npm", "run", "dev"]
DOCKER

cat > dropp-web/package.json << 'JSON'
{
  "name": "dropp-web",
  "version": "1.0.0",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "next": "14.2.15",
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "typescript": "^5.6.3",
    "@types/node": "^22.7.5",
    "@types/react": "^18.3.11",
    "@types/react-dom": "^18.3.0",
    "tailwindcss": "^3.4.13",
    "postcss": "^8.4.47",
    "autoprefixer": "^10.4.20"
  }
}
JSON

cat > dropp-web/tsconfig.json << 'JSON'
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": { "@/*": ["./src/*"] }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
JSON

cat > dropp-web/tailwind.config.js << 'JS'
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx}"],
  theme: { extend: {} },
  plugins: [],
}
JS

cat > dropp-web/postcss.config.js << 'JS'
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
JS

echo "Stage 1 files created successfully."
