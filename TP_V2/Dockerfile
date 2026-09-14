FROM python:3.11-alpine

WORKDIR /code

COPY requirements.txt /code
RUN  pip3 install -r requirements.txt

COPY main.py /code

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
