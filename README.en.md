# Homework #14

In this task, we continue to refine our REST API application from home [task 13](https://github.com/Goit-Home-Works/Py_WEB_13).

## Assignment

1. Create documentation for your homework using Sphinx. To do this, add docstrings to the necessary functions and methods of classes.

2. Unit test your homework repository modules using the Unittest framework. Take as a basis the example from the note for the module `tests/test_unit_repository_notes.py`.

3. Functionally test any route of your choice from your homework using the pytest framework.

## Additional task

4. Cover your homework with tests more than 95%. Use the `pytest-cov' package to check.
   

## Execution
Before running the script, remember to set your SendGrid API key in the SENDGRID_API_KEY environment variable. If you're using a Unix-like system, you can set it like this:

```bash
echo "export SENDGRID_API_KEY='YOUR_API_KEY'" > sendgrid.env
echo "sendgrid.env" >> .gitignore
source ./sendgrid.env
```
Replace 'YOUR_API_KEY' with your actual SendGrid API key.

To run the program, copy and paste the following command into the terminal:

```bash
python3 src/main.py
```
1. Click on Sphinx DOC.

2. To run unittest, copy and paste the following command into the terminal:
```
python3 unittest/repository_contacts_unit_test.py
```

3.To run pytest-cov, copy and paste the following command into the terminal:




```
poetry run pytest -v -p no:warnings --cov=. --cov-report term pytest/
```
or

```
pytest -v -p no:warnings --cov=. --cov-report term pytest/
```
