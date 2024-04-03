###Бот подсчитывает членские взносы в клубе
####Установить 
```
pip install pyTelegramBotAPI
pip install python-dotenv
```

Cоздайтm файл .env в том же каталоге, где находится bot.py, и добавьте в него следующие строки 
```
TOKEN=<TOKEN>
MEMBERSHIP_FEE=<MEMBERSHIP_FEE>
ADMIN_CHAT_ID=<ADMIN_CHAT_ID>,<ADMIN_CHAT_ID>
```
(заменить <TOKEN> и <MEMBERSHIP_FEE> на токен Telegram и сумму членского взноса):

Чтобы обеспечить постоянную работу скрипта даже после завершения сеанса входа в систему. Используем системный менеджер служб.

Вот как вы можно сделать это на Linux-системах с использованием systemd в качестве системного менеджера служб:
Создайть файл службы. Например, my_telegram_bot.service, в директории /etc/systemd/system/.

```
[Unit]
Description=My Telegram Bot
After=network.target

[Service]
Type=simple
User=my_user
WorkingDirectory=/path/to/your/bot/directory
ExecStart=/usr/bin/python3 bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```
В этом файле my_telegram_bot.service нужно заменить 
User на имя пользователя, под которым будет запускаться скрипт, и 
WorkingDirectory на путь к директории, где расположен скрипт. 
Также указать полный путь к исполняемому файлу Python в ExecStart.

После создания файла службы, запустить следующую команду, чтобы перезагрузить systemd и добавить службу:
```
sudo systemctl daemon-reload
```

Теперь вы можно запустить службу с помощью следующей команды:
```
sudo systemctl start my_telegram_bot
```

Также можно настроить автоматический запуск службы при загрузке системы:
```
sudo systemctl enable my_telegram_bot
```

После выполнения этих шагов телеграм-бот будет работать в фоновом режиме, независимо от того, авторизован пользователь или в системе или нет.

