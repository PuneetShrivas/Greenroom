FROM python:3.11.9

#
WORKDIR /code

#
COPY ./requirements.txt /code/requirements.txt

#
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

#
COPY ./app /code/app
COPY ./core /code/core
COPY ./data /code/data
COPY ./testing /code/testing
COPY ./main.py /code/main.py


CMD ["fastapi", "run", "main.py"]