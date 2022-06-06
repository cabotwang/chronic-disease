from hydralit import HydraApp
import streamlit as st
from datasearch import datasearchApp
from datainput import datainputApp
from followup import followupApp
from medhis import medhisApp

st.set_page_config(layout="wide", initial_sidebar_state='collapsed')
for line in open('style.css', encoding='utf-8'):
    st.markdown(f'<style>{line}</style>', unsafe_allow_html=True)

if __name__ == '__main__':
    st.title('来宾个案管理平台')
    app = HydraApp(title='慢病管理平台', favicon="🏠", navbar_theme={'menu_background':'royalblue'})
    app.add_app("院前信息采集", icon="⌨", app=datainputApp())
    app.add_app("院中信息记录", icon="🛏️", app=medhisApp())
    app.add_app("院后信息随访", icon="📅", app=followupApp())
    app.add_app("信息查询", icon="📚", app=datasearchApp())

    app.run()
