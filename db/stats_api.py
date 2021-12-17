import traceback
from collections import Counter

import pymongo
import streamlit as st

from db.connection import CONNECTION_STRING


def get_stats():
    client = None
    try:
        client = pymongo.MongoClient(CONNECTION_STRING)
        db = client.get_database(st.secrets['DB_NAME'])
        collection = db.get_collection(st.secrets['COLLECTION_MATCHES'])
        matches = collection.find()

        goal_counter = Counter()
        assist_counter = Counter()
        win_count, tie_count, lose_count = 0, 0, 0
        total_goals, total_conceded = 0, 0

        for match in matches:
            if match['player_num'] != 0:
                if match['scored'] > match['conceded']:
                    win_count += 1
                elif match['scored'] < match['conceded']:
                    lose_count += 1
                else:
                    tie_count += 1
            total_goals += match['scored']
            total_conceded += match['conceded']
            goal_counter.update(match['score_list'])
            assist_counter.update(match['assist_list'])

        return {
            'most_goals': goal_counter.most_common(3), 'most_assists': assist_counter.most_common(3),
            'win_count': win_count, 'lose_count': lose_count, 'tie_count': tie_count,
            'total_goals': total_goals, 'total_conceded': total_conceded
        }
    except:
        traceback.print_exc()
        raise Exception
    finally:
        if client is not None:
            client.close()


