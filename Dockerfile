FROM python:3.9.13-slim-bullseye
WORKDIR /usr/src/app/
COPY requirements.txt req.txt
RUN pip3 install -r req.txt
COPY . .
CMD ["python3", "server.py"]