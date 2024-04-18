
# Домашнє завдання #14

У цьому завданні ми продовжуємо доопрацьовувати наш REST API застосунок із домашнього [завдання 13](https://github.com/Goit-Home-Works/Py_WEB_13).

## Завдання

1. Створіть документацію для вашого домашнього завдання за допомогою Sphinx. Для цього додайте до необхідних функцій і методів класів рядки docstrings.

2. Покрийте модульними тестами модулі репозиторію вашого домашнього завдання, використовуючи фреймворк Unittest. За основу візьміть приклад із конспекту для модуля `tests/test_unit_repository_notes.py`.

3. Покрийте функціональними тестами будь-який маршрут на вибір з вашого домашнього завдання, використовуючи фреймворк pytest.

## Додаткове завдання

4. Покрийте ваше домашнє завдання тестами більш ніж на 95%. Для контролю використовуйте пакет `pytest-cov`.

## Виконання

Remember to set your SendGrid API key in the SENDGRID_API_KEY environment variable before running the script. If you're using a Unix-like system, you can set it like this:

```bash
echo "export SENDGRID_API_KEY='YOUR_API_KEY'" > sendgrid.env
echo "sendgrid.env" >> .gitignore
source ./sendgrid.env
```
Replace 'YOUR_API_KEY' with your actual SendGrid API key.

Щоб запустити програму, скопіюйте та вставте наступну команду у термінал:

```bash
python3 src/main.py
```
1. Натиснить на Sphinx DOC

2. Щоб запустити unittest, скопіюйте та вставте наступну команду у термінал:
```
python3 unittest/repository_contacts_unit_test.py
```

3. Щоб запустити pytest-cov, скопіюйте та вставте наступну команду у термінал:


```
poetry run pytest -v -p no:warnings --cov=. --cov-report term pytest/
```
or

```
pytest -v -p no:warnings --cov=. --cov-report term pytest/
```
