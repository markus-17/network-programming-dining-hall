FROM python:3.9.0

COPY * .

RUN pip install requests flask

EXPOSE 8080

CMD ["python", "-u", "main.py"]