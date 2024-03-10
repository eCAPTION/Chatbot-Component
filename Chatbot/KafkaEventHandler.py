from ecaption_utils.kafka.faust import get_faust_app, FaustApplication, initialize_topics
from ecaption_utils.kafka.topics import Topic, get_event_type
from kafka import KafkaProducer
import re
import config
import NewsVisualizerBot

app = get_faust_app(FaustApplication.Chatbot, config.FAUST_APP_BROKER_URL, config.FAUST_APP_WEB_PORT)
topics = initialize_topics(
    app,
    [
        Topic.NEW_ARTICLE_URL,
        Topic.ADD_INSTRUCTION,
        Topic.DELETE_INSTRUCTION,
        Topic.NEW_INFOGRAPHIC,
        Topic.MODIFIED_INFOGRAPHIC,
        Topic.ERROR,
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


@app.agent(topics[Topic.NEW_ARTICLE_URL])
async def handle_article_url(event_stream):
    async for event in event_stream:
        article_text = event.url
        print(f'This is the article text: {article_text}')
        request_id = event.request_id
        print(f'This is the request ID: {request_id}')


@app.agent(topics[Topic.ADD_INSTRUCTION])
async def handle_add_instruction(event_stream):
    async for event in event_stream:
        print('----------------DELETE_INSTRUCTION---------------')
        request_id = event.request_id
        print(f'This is the request ID: {request_id}')
        infographic_link = event.infographic_link
        print(f'This is the infographic link: {infographic_link}')
        target_element = event.target_element
        print(f'This is the target element: {target_element}')
        infographic_section = event.infographic_section
        print(f'This is the infographic section: {infographic_section}')


@app.agent(topics[Topic.DELETE_INSTRUCTION])
async def handle_delete_instruction(event_stream):
    async for event in event_stream:
        print('----------------DELETE_INSTRUCTION---------------')
        request_id = event.request_id
        print(f'This is the request ID: {request_id}')
        infographic_link = event.infographic_link
        print(f'This is the infographic link: {infographic_link}')
        infographic_section = event.infographic_section
        print(f'This is the infographic section: {infographic_section}')


def emit_intermediate_representation(intermediate_representation, infographic_link, request_id):
    if intermediate_representation['instruction_type'] == 'ADD':
        emit_add_intermediate_representation(intermediate_representation['target_element'],
                                             intermediate_representation['infographic_section'],
                                             infographic_link, request_id)
    elif intermediate_representation['instruction_type'] == 'DELETE':
        emit_delete_intermediate_representation(intermediate_representation['infographic_section'],
                                                infographic_link, request_id)


def emit_add_intermediate_representation(target_element, infographic_section, infographic_link, request_id):
    topic = Topic.ADD_INSTRUCTION
    Event = get_event_type(topic)
    pattern = r'\'(.*?)\''
    matches = re.findall(pattern, str(Event))
    class_name = matches[0]
    faust_ns_value = f'"ns":"{class_name}"'
    faust_value = '"__faust":{' + faust_ns_value + '}'
    value = '{' + f'"request_id":{request_id},"infographic_link":"{infographic_link}","target_element":"{target_element}","infographic_section":"{infographic_section}",{faust_value}' + '}'

    producer = KafkaProducer(bootstrap_servers='localhost:9092')
    producer.send(topic.value, str.encode(value))
    producer.close()


def emit_delete_intermediate_representation(infographic_section, infographic_link, request_id):
    topic = Topic.DELETE_INSTRUCTION
    Event = get_event_type(topic)
    pattern = r'\'(.*?)\''
    matches = re.findall(pattern, str(Event))
    class_name = matches[0]
    faust_ns_value = f'"ns":"{class_name}"'
    faust_value = '"__faust":{' + faust_ns_value + '}'
    value = '{' + f'"request_id":{request_id},"infographic_link":"{infographic_link}","infographic_section":"{infographic_section}",{faust_value}' + '}'

    producer = KafkaProducer(bootstrap_servers='localhost:9092')
    producer.send(topic.value, str.encode(value))
    producer.close()


@app.agent(topics[Topic.ERROR])
async def handle_error(event_stream):
    async for event in event_stream:
        error_type = event.error_type
        if error_type == FaustApplication.WebScraper.value:
            request_id = event.request_id
            error_message = event.error_message
            NewsVisualizerBot.send_error_message_article_link(request_id, error_message)


@app.agent(topics[Topic.NEW_INFOGRAPHIC])
async def handle_new_infographic(event_stream):
    async for event in event_stream:
        request_id = event.request_id
        infographic_link = event.infographic_link
        NewsVisualizerBot.send_new_infographic(request_id, infographic_link)


@app.agent(topics[Topic.MODIFIED_INFOGRAPHIC])
async def handle_modified_infographic(event_stream):
    async for event in event_stream:
        request_id = event.request_id
        new_infographic_link = event.new_infographic_link
        NewsVisualizerBot.send_modified_infographic(request_id, new_infographic_link)

