from hydralit import HydraApp
import streamlit as st
from datasearch import datasearchApp
from data_input import datainputApp
from model_explain import modelexplainApp

st.set_page_config(layout="wide")


if __name__ == '__main__':
    # this is the host application, we add children to it and that's it!
    st.title('来宾慢病管理平台')
    app = HydraApp(title='慢病管理平台', favicon="🏠", navbar_theme={'menu_background':'royalblue'})
    app.add_app("信息采集", icon="⌨", app=datainputApp())
    app.add_app("信息查询", icon="📚", app=datasearchApp())
    app.add_app("诊疗路径", icon="💬", app=modelexplainApp())

    # run the whole lot
    app.run()
