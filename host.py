from Widget.Hydralit import HydraApp
import streamlit as st
from datasearch import datasearchApp
from datainput import datainputApp
from followup import followupApp
from medhis import medhisApp

st.set_page_config(layout="wide", initial_sidebar_state='collapsed')
for line in open('style.css', encoding='utf-8'):
    st.markdown(f'<style>{line}</style>', unsafe_allow_html=True)

if __name__ == '__main__':

    app = HydraApp(title='慢病管理平台', favicon="🏠", navbar_theme={'menu_background':'royalblue'})
    app.add_app("我的病人", icon="📚", app=datasearchApp())
    app.add_app("院前信息采集", icon="⌨", app=datainputApp())
    app.add_app("住院信息记录", icon="🛏️", app=medhisApp())
    app.add_app("院后信息随访", icon="📅", app=followupApp())

    app.run()
