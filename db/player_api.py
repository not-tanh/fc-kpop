import traceback

import pymongo
import streamlit as st
from bson.objectid import ObjectId

from objects.player import Player
from db.connection import CONNECTION_STRING


def create_player(player: Player):
    client = None
    try:
        client = pymongo.MongoClient(CONNECTION_STRING)
        db = client.get_database(st.secrets['DB_NAME'])
        collection = db.get_collection(st.secrets['COLLECTION_PLAYERS'])
        collection.insert_one(player.__dict__)
    except:
        traceback.print_exc()
        raise Exception
    finally:
        if client is not None:
            client.close()


def update_player(object_id: str, player: Player):
    client = None
    try:
        client = pymongo.MongoClient(CONNECTION_STRING)
        db = client.get_database(st.secrets['DB_NAME'])
        collection = db.get_collection(st.secrets['COLLECTION_PLAYERS'])
        collection.update_one({'_id': ObjectId(object_id)}, {'$set': player.__dict__})
    except:
        traceback.print_exc()
        raise Exception
    finally:
        if client is not None:
            client.close()


@st.experimental_memo(ttl=120)
def get_players():
    client = None
    try:
        client = pymongo.MongoClient(CONNECTION_STRING)
        db = client.get_database(st.secrets['DB_NAME'])
        collection = db.get_collection(st.secrets['COLLECTION_PLAYERS'])
        result = collection.find()
        return list(result)
    except:
        traceback.print_exc()
        raise Exception
    finally:
        if client is not None:
            client.close()
