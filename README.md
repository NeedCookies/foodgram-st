### 1. Скачиваем репозиторий
* ```git clone https://github.com/NeedCookies/foodgram-st```  
* ```cd foodgram-st```  
  
### 2. Запускаем все сервисы
* ```cd infra```  
* ```https://github.com/NeedCookies/foodgram-st```

### 3. Создаем суперпользователя
* ```sudo docker-compose exec backend python manage.py createsuperuser```

### 4. Загружаем ингриенты в Постгрю в докере
* ```sudo docker-compose exec backend python manage.py load_ingredients data/ingredients.json```

### 5. Проект готов

* Главная страница: http://localhost
* Админка: http://localhost/admin 

### *Дополнительно посмотреть базу данных в PgAdmin*
1) Заходим на `localhost:5050`
2) Вводим логин: `admin@example.com`, пароль: `admin`
3) Регистрируем нашу БД, во вкладке ***Connection*** вводим данные:
   ![Снимок экрана от 2025-06-30 00-49-55](https://github.com/user-attachments/assets/d1ef3e8b-67f5-44f3-ad22-0c68046620e9)


## Переменные окружения (ENV)

```bash
cd infra
touch .env
```
В файл .env добавляем:
```ini
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,foodgram-backend

POSTGRES_DB=foodgram-db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

PAGE_SIZE=6
