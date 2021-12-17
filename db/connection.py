import streamlit as st

CONNECTION_STRING = f'mongodb+srv://{st.secrets["DB_USERNAME"]}:{st.secrets["DB_PASSWORD"]}@instacheckercluster.' \
                    f'zg7xn.mongodb.net/instachecker?retryWrites=true&w=majority'
