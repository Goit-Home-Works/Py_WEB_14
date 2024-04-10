

# Define the base image
FROM python:3.11

# Set environment variables
ENV APP_HOME /app

# Set the working directory inside the container
WORKDIR $APP_HOME

# Copy the Python requirements file
COPY requirements.txt requirements.txt

# Install dependencies inside the container
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set the execution permissions for the run script
# COPY run.sh run.sh
# RUN chmod +x run.sh

# Define the command to run the application when the container starts
# CMD ["./run.sh"]
CMD ["python", "./src/main.py"]
