# Homework Assignment #13

## Part 1

In this homework assignment, we continue to refine our REST API application based on [Homework 12](https://github.com/Goit-Home-Works/Py_WEB_12).

### Task

- Implement an email verification mechanism for registered users.
- Limit the number of requests to your contact routes. Ensure rate limiting - limiting the creation of contacts for a user.
- Enable CORS for your REST API.
- Implement the ability to update a user's avatar. Use the Cloudinary service.

### General Requirements

- All environment variables should be stored in a `.env` file. There should be no sensitive data in plain text within the code.
- To run all services and databases for the application, use Docker Compose.

### Bonus Task

- Implement a caching mechanism using Redis database. Cache the current user during authentication.
- Implement a password reset mechanism for the REST API application.

## Part 2

In this homework assignment, we continue to refine our Django application based on [Homework 10](link_to_homework_10).

### Task

- Implement a password reset mechanism for a registered user.
- All environment variables should be stored in a `.env` file and used in the `settings.py` file.

## Execution

Remember to set your SendGrid API key in the SENDGRID_API_KEY environment variable before running the script. If you're using a Unix-like system, you can set it like this:

```bash
echo "export SENDGRID_API_KEY='YOUR_API_KEY'" > sendgrid.env
echo "sendgrid.env" >> .gitignore
source ./sendgrid.env
```
Replace 'YOUR_API_KEY' with your actual SendGrid API key.

To run the program, copy and paste the following command into your terminal:

```bash
python3 src/main.py
```

After that, click on API DOC button.


## OR in docker:
## Installation and launch
### Prepare to change the .env environment
Based on the example [.env_example](.env-example), create files with your individual data:
- .env (defines APP_ENV that defines the current working file is prod, dev)
- .env-dev (Settings for dev)
- .env-prod (Settings for prod)

Run the script:

```
docker compose --env-file .env-dev --file docker-compose-db.yml up -d
cd ./src && alembic upgrade head
```

#### FastAPI server
Run the script:
```
cd ./src
uvicorn main:app --reload --port 9000
```
or
```
cd ./src
python3 ./main.py
```


### Open the browser page http://localhost:9000