import pymongo
from dotenv import load_dotenv
import os

load_dotenv()

db_connection_string = os.getenv("DB_CONNECTION_STRING")
db_admin_username = os.getenv("DB_ADMIN_USERNAME")
db_admin_pw = os.getenv("DB_ADMIN_PW")
db_database_name = os.getenv("DB_DATABASE_NAME")
db_articles_collection_name = os.getenv("DB_ARTICLES_COLLECTION_NAME")
db_infographics_collection_name = os.getenv("DB_INFOGRAPHICS_COLLECTION_NAME")
db_requests_collection_name = os.getenv("DB_REQUESTS_COLLECTION_NAME")


def startup_database():
    print("Initializing News Articles Database...")

    # Initialise MongoDB cluster
    mongodb_connection_url = db_connection_string.format(
        db_admin_username,
        db_admin_pw
    )
    mongodb_client = pymongo.MongoClient(mongodb_connection_url)

    database = mongodb_client[db_database_name]
    return database


def send_existing_news_article_infographic(database, chat_id, news_article):
    news_articles_collection = database[db_articles_collection_name]
    existing_news_article_document = fetch_existing_news_article_document(chat_id, news_article,
                                                                          news_articles_collection)
    return existing_news_article_document['link_to_infographic']


def check_if_news_article_infographic_exist(database, chat_id, news_article):
    news_articles_collection = database[db_articles_collection_name]
    query = {
        "chat_id": chat_id,
        "article_link": news_article
    }
    news_article_document = news_articles_collection.find_one(query)
    if news_article_document:
        return True
    else:
        return False


def create_news_article_document(database, chat_id, news_article_link):
    news_articles_collection = database[db_articles_collection_name]
    news_article_document = {
        "chat_id": chat_id,
        "article_link": news_article_link,
        "link_to_infographic": ''
    }
    news_articles_collection.insert_one(news_article_document)


def fetch_existing_news_article_document(chat_id, news_article_link, news_articles_collection):
    query = {
        "chat_id": chat_id,
        "article_link": news_article_link
    }
    news_article_document = news_articles_collection.find_one(query)
    return news_article_document


def add_infographic_to_article(database, chat_id, article_link, infographic_link):
    news_articles_collection = database[db_articles_collection_name]
    query = {
        "chat_id": chat_id,
        "article_link": article_link
    }
    update = {
        "$set": {
            "link_to_infographic": infographic_link
        }
    }
    news_articles_collection.update_one(query, update)

    infographics_collection = database[db_infographics_collection_name]
    infographic_document = create_infographic_document(infographic_link)
    infographics_collection.insert_one(infographic_document)


def create_infographic_document(link_to_infographic):
    infographic_document = {
        "link_to_infographic": link_to_infographic,
        "unreliable_vote_count": 0,
        "reliable_vote_count": 0,
        "share_count": 1,
        "comments": [],
    }
    return infographic_document


def check_if_infographic_link_exists(database, link_to_infographic):
    infographics_collection = database[db_infographics_collection_name]
    query = {
        "link_to_infographic": link_to_infographic
    }
    infographic_document = infographics_collection.find_one(query)
    if infographic_document:
        return True
    else:
        return False


def update_infographic_of_article(database, chat_id, old_infographic_link, new_infographic_link):
    news_articles_collection = database[db_articles_collection_name]
    query = {
        "chat_id": chat_id,
        "link_to_infographic": old_infographic_link
    }
    update = {
        "$set": {
            "link_to_infographic": new_infographic_link
        }
    }
    news_articles_collection.update_one(query, update)

    infographics_collection = database[db_infographics_collection_name]
    infographic_document = create_infographic_document(new_infographic_link)
    infographics_collection.insert_one(infographic_document)


def increase_share_count(database, link_to_infographic):
    infographics_collection = database[db_infographics_collection_name]
    query = {
        "link_to_infographic": link_to_infographic
    }
    infographic_document = infographics_collection.find_one(query)
    original_share_count = infographic_document['share_count']
    update = {
        "$set": {
            "share_count": original_share_count + 1
        }
    }
    status = infographics_collection.update_one(query, update)

    if status.modified_count == 1:
        print("Document updated successfully!")
    else:
        print("Document not found or no changes made.")


def increase_reliable_vote_count(database, link_to_infographic):
    infographics_collection = database[db_infographics_collection_name]
    query = {
        "link_to_infographic": link_to_infographic
    }
    infographic_document = infographics_collection.find_one(query)
    original_reliable_vote_count = infographic_document['reliable_vote_count']
    update = {
        "$set": {
            "reliable_vote_count": original_reliable_vote_count + 1
        }
    }
    status = infographics_collection.update_one(query, update)

    if status.modified_count == 1:
        print("Document updated successfully!")
    else:
        print("Document not found or no changes made.")


def increase_unreliable_vote_count(database, link_to_infographic):
    infographics_collection = database[db_infographics_collection_name]
    query = {
        "link_to_infographic": link_to_infographic
    }
    infographic_document = infographics_collection.find_one(query)
    original_unreliable_vote_count = infographic_document['unreliable_vote_count']
    update = {
        "$set": {
            "unreliable_vote_count": original_unreliable_vote_count + 1
        }
    }
    status = infographics_collection.update_one(query, update)

    if status.modified_count == 1:
        print("Document updated successfully!")
    else:
        print("Document not found or no changes made.")


def get_infographic_document(database, link_to_infographic):
    infographics_collection = database[db_infographics_collection_name]
    query = {
        "link_to_infographic": link_to_infographic
    }
    infographic_document = infographics_collection.find_one(query)
    return infographic_document


def add_comment(database, link_to_infographic, comment):
    infographics_collection = database[db_infographics_collection_name]
    query = {
        "link_to_infographic": link_to_infographic
    }
    infographic_document = infographics_collection.find_one(query)
    existing_comments = infographic_document['comments']
    existing_comments.append(comment)
    update = {
        "$set": {
            "comments": existing_comments
        }
    }
    status = infographics_collection.update_one(query, update)

    if status.modified_count == 1:
        print("Document updated successfully!")
    else:
        print("Document not found or no changes made.")


def assign_request_news_article(database, chat_id, article_link):
    requests_collection = database[db_requests_collection_name]
    current_request_count = requests_collection.count_documents({})
    allocated_request_id = current_request_count + 1
    request_document = {
        "chat_id": chat_id,
        "request_id": allocated_request_id,
        "article_link": article_link,
        "infographic_link": '',
        "user_instruction": '',
    }
    requests_collection.insert_one(request_document)
    return allocated_request_id


def assign_request_infographic_changes(database, chat_id, infographic_link, user_instruction):
    requests_collection = database[db_requests_collection_name]
    current_request_count = requests_collection.count_documents({})
    allocated_request_id = current_request_count + 1
    request_document = {
        "chat_id": chat_id,
        "request_id": allocated_request_id,
        "article_link": '',
        "infographic_link": infographic_link,
        "user_instruction": user_instruction,
    }
    requests_collection.insert_one(request_document)
    return allocated_request_id


def get_request(database, request_id):
    requests_collection = database[db_requests_collection_name]
    query = {
        "request_id": request_id
    }
    request_document = requests_collection.find_one(query)
    return request_document
