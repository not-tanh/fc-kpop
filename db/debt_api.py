import traceback

import pymongo
import streamlit as st
from bson.objectid import ObjectId

from objects.debt import Debt
from db.connection import CONNECTION_STRING


def create_debt(debt: Debt):
    client = None
    try:
        client = pymongo.MongoClient(CONNECTION_STRING)
        db = client.get_database(st.secrets['DB_NAME'])
        collection = db.get_collection(st.secrets['COLLECTION_DEBT'])
        collection.insert_one(debt.__dict__)
    except:
        traceback.print_exc()
        raise Exception
    finally:
        if client is not None:
            client.close()


def update_debt(object_id: ObjectId, debt: Debt):
    client = None
    try:
        client = pymongo.MongoClient(CONNECTION_STRING)
        db = client.get_database(st.secrets['DB_NAME'])
        collection = db.get_collection(st.secrets['COLLECTION_DEBT'])
        collection.update_one({'_id': object_id}, {'$set': debt.__dict__})
    except:
        traceback.print_exc()
        raise Exception
    finally:
        if client is not None:
            client.close()


def delete_debt(object_ids: list[ObjectId]):
    client = None
    try:
        client = pymongo.MongoClient(CONNECTION_STRING)
        db = client.get_database(st.secrets['DB_NAME'])
        collection = db.get_collection(st.secrets['COLLECTION_DEBT'])
        collection.delete_many({'_id': {'$in': object_ids}})
    except:
        traceback.print_exc()
        raise Exception
    finally:
        if client is not None:
            client.close()


@st.experimental_memo(ttl=120, show_spinner=False)
def get_debt():
    client = None
    try:
        client = pymongo.MongoClient(CONNECTION_STRING)
        db = client.get_database(st.secrets['DB_NAME'])
        collection = db.get_collection(st.secrets['COLLECTION_DEBT'])
        result = collection.find()
        grouped_result = dict()
        for r in result:
            if r['player_id'] not in grouped_result:
                grouped_result[r['player_id']] = dict()
                grouped_result[r['player_id']]['sum'] = 0
                grouped_result[r['player_id']]['detail'] = []
            grouped_result[r['player_id']]['detail'].append(r)
            grouped_result[r['player_id']]['sum'] += r['value']
        return grouped_result
    except:
        traceback.print_exc()
        raise Exception
    finally:
        if client is not None:
            client.close()
