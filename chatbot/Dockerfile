FROM python:3.10

COPY chatbot/requirements.txt .
RUN pip install -r requirements.txt
RUN pip install --upgrade black
RUN pip install --upgrade click
COPY . .
COPY kafka_io_logic .

WORKDIR /chatbot
CMD ["python", "-u", "NewsVisualizerBot.py"]
