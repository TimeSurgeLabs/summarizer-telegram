FROM python:3.10-slim-buster

# install pipenv and update pip
RUN pip install --upgrade pipenv pip

COPY . .

# install requirements to system
RUN pipenv install --system --deploy --ignore-pipfile

# run the app
CMD ["python", "main.py"]
