FROM python:3.11

COPY kafka_io_logic/requirements.txt .
RUN pip install -r requirements.txt
RUN pip install --upgrade faust-streaming
COPY . .
COPY chatbot .

EXPOSE 29092

WORKDIR /kafka_io_logic
CMD ["sh", "-c", "exec faust -A KafkaEventHandler worker -l info"]
