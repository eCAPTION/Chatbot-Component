import pymongo
import config

def startup_database():
    print("Initializing News Articles Database...")

    # Initialise MongoDB cluster
    mongodb_connection_url = config.DB_CONNECTION_STRING.format(
        config.DB_ADMIN_USERNAME,
        config.DB_ADMIN_PW
    )
    mongodb_client = pymongo.MongoClient(mongodb_connection_url)

    database = mongodb_client[config.DB_DATABASE_NAME]
    return database

def receive_news_article(database, chat_id, news_article):
    news_articles_collection = database[config.DB_ARTICLES_COLLECTION_NAME]

    existing_news_article_document = fetch_existing_news_article_document(chat_id, news_article, news_articles_collection)
    if existing_news_article_document:
        return existing_news_article_document['link_to_infographic']
    else:
        news_article_document = create_news_article_document(chat_id, news_article)
        news_articles_collection.insert_one(news_article_document)
        link_to_infographic = news_article_document['link_to_infographic']

        infographics_collection = database[config.DB_INFOGRAPHICS_COLLECTION_NAME]
        infographic_document = create_infographic_document(link_to_infographic)
        infographics_collection.insert_one(infographic_document)
        return link_to_infographic

def create_news_article_document(chat_id, news_article_link):
    # TODO: Generate a unique link to access the infographic, after receiving the generated infographic
    link_to_infographic = 'b'
    news_article_document = {
        "chat_id": chat_id,
        "article_link": news_article_link,
        "link_to_infographic": link_to_infographic
    }
    return news_article_document

def fetch_existing_news_article_document(chat_id, news_article_link, news_articles_collection):
    query = {
        "chat_id": chat_id,
        "article_link": news_article_link
    }
    news_article_document = news_articles_collection.find_one(query)
    return news_article_document

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
    infographics_collection = database[config.DB_INFOGRAPHICS_COLLECTION_NAME]
    query = {
        "link_to_infographic": link_to_infographic
    }
    infographic_document = infographics_collection.find_one(query)
    if infographic_document:
        return True
    else:
        return False

def increase_share_count(database, link_to_infographic):
    infographics_collection = database[config.DB_INFOGRAPHICS_COLLECTION_NAME]
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
    infographics_collection = database[config.DB_INFOGRAPHICS_COLLECTION_NAME]
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
    infographics_collection = database[config.DB_INFOGRAPHICS_COLLECTION_NAME]
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
    infographics_collection = database[config.DB_INFOGRAPHICS_COLLECTION_NAME]
    query = {
        "link_to_infographic": link_to_infographic
    }
    infographic_document = infographics_collection.find_one(query)
    return infographic_document

def add_comment(database, link_to_infographic, comment):
    infographics_collection = database[config.DB_INFOGRAPHICS_COLLECTION_NAME]
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
