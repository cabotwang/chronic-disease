import datetime
from deta import Deta
import streamlit as st

deta = Deta(st.secrets["deta_key"])
db_info = deta.Base("test")
id = '12344'
dict1 = {'A': 'abc', 'B': 'cdf', 'C': datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")}
print('{id}_{symptom}_{type}_{time}'.format(id=id, symptom=dict1['A'], type=dict1['B'], time=dict1['C']))

db_info.put({"key": "user-a", "username": "jimmy",
  "profile": [{
    "age": 32,
    "active": False,
    "hometown": "pittsburgh"
  }, {
    "age": 33,
    "active": True,
    "hometown": "pittsburgh"}],
  "on_mobile": True,
  "likes": ["anime"],
  "purchases": 1
})
