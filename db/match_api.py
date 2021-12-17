import traceback
from bson.objectid import ObjectId

import pymongo
import streamlit as st

from objects.match import Match
from db.connection import CONNECTION_STRING


def create_match(match: Match):
    client = None
    try:
        client = pymongo.MongoClient(CONNECTION_STRING)
        db = client.get_database(st.secrets['DB_NAME'])
        collection = db.get_collection(st.secrets['COLLECTION_MATCHES'])
        collection.insert_one(match.__dict__)
    except:
        traceback.print_exc()
        raise Exception
    finally:
        if client is not None:
            client.close()


@st.experimental_memo(ttl=120)
def get_matches():
    client = None
    try:
        client = pymongo.MongoClient(CONNECTION_STRING)
        db = client.get_database(st.secrets['DB_NAME'])
        collection = db.get_collection(st.secrets['COLLECTION_MATCHES'])
        result = collection.find()
        return list(result)[::-1]
    except:
        traceback.print_exc()
        raise Exception
    finally:
        if client is not None:
            client.close()


def update_match(object_id: ObjectId, match: Match):
    client = None
    try:
        client = pymongo.MongoClient(CONNECTION_STRING)
        db = client.get_database(st.secrets['DB_NAME'])
        collection = db.get_collection(st.secrets['COLLECTION_MATCHES'])
        collection.update_one({'_id': object_id}, {'$set': match.__dict__})
    except:
        traceback.print_exc()
        raise Exception
    finally:
        if client is not None:
            client.close()
