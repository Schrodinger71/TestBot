# 🤖 TestBot  

## 👤 Автор:  
- Discord: **schrodinger71** (id:328502766622474240)  
- GitHub: [@Schrodinger71](https://github.com/Schrodinger71)  

TestBot — это универсальный Discord-бот для тестирования различных функций, интеграций и API. Он предоставляет безопасную песочницу для экспериментов с Discord.py, GitHub Actions и другими сервисами.  

---

## 📦 Основные возможности  

- 🧪 **Тестовые команды** для проверки функционала Discord.py  
- ⚙️ **Интеграция с GitHub API** (проверка workflow статусов)  
- 📊 **Логирование** (сохранение тестовых данных)  
- 🔄 **Автоматический рестарт** при обнаружении изменений в репозитории

---

## 🚀 Быстрый старт  

1. Клонируйте репозиторий:  
   ```bash  
   git clone https://github.com/Schrodinger71/TestBot.git  
   cd TestBot  
   ```  

2. Установите зависимости:  
   ```bash  
   pip install -r requirements.txt  
   ```  

3. Настройте конфигурацию:  
   - Создайте файл `.env` и добавьте:  
     ```  
     DISCORD_TOKEN=ваш_токен_бота  
     GITHUB_TOKEN=ваш_github_token (опционально)  
     ```  

4. Запустите бота:  
   ```bash  
   python main.py  
   ```  

---


---

## 📌 Важные особенности  

- 🔒 **Безопасность**: Все команды работают только в тестовых каналах.  
- ♻️ **Автообновление**: Бот может автоматически перезагружаться при изменении кода (через `watchdog`).(В ПРОЦЕССЕ)

--- 

## 🛠 Техническая информация  

### Структура проекта  
```  
TestBot/  
├── main.py            # Основной скрипт  
├── commands/          # Тестовые команды  
│   ├── basic.py       # Базовые команды  
│   └── voice.py       # Управление голосом  
├── utils/             # Вспомогательные скрипты  
│   └── logger.py      # Система логирования  
└── requirements.txt   # Зависимости (Discord.py, python-dotenv)  
```  
