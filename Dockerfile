FROM python:3.7

WORKDIR /usr/src/mjm_parsing

# Установить зависимости приложения
# Используется символ подстановки для копирования как package.json, так и package-lock.json,
# работает с npm@5+
# COPY package*.json ./

RUN pip install -r requirements.txt
# Используется при сборке кода в продакшене
# RUN npm install --only=production
COPY . .


EXPOSE 5000

CMD [ "flask", "run" ]
