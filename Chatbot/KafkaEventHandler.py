from ecaption_utils.kafka.faust import get_faust_app, initialize_topics, FaustApplication
from ecaption_utils.kafka.topics import Topic, get_event_type
from kafka import KafkaProducer
import re

app = get_faust_app(FaustApplication.Chatbot)
topics = initialize_topics(
    app,
    [
        Topic.NEW_ARTICLE_URL,
    ],
)

def emit_article_url(article_url, request_id):
    topic = Topic.NEW_ARTICLE_URL
    Event = get_event_type(topic)
    pattern = r'\'(.*?)\''
    matches = re.findall(pattern, str(Event))
    class_name = matches[0]
    faust_ns_value = f'"ns":"{class_name}"'
    faust_value = '"__faust":{' + faust_ns_value + '}'
    value = '{' + f'"url":"{article_url}","request_id":{request_id},{faust_value}' + '}'

    producer = KafkaProducer(bootstrap_servers='localhost:9092')
    producer.send("new_article_url", str.encode(value))
    producer.close()

