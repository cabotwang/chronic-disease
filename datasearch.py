import streamlit as st
import pandas as pd
from hydralit import HydraHeadApp
from deta import Deta
import time

# # .streamlit/secrets.toml
# AWS_ACCESS_KEY_ID = "AKIAS25PCSD2GRJVSB5W"
# AWS_SECRET_ACCESS_KEY = "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"


class datasearchApp(HydraHeadApp):
    def run(self):
        st.markdown("""
        <style>
        .label-font {
            font-size:20px; font:sans serif; font-weight:700; 
        }
        </style>
        """, unsafe_allow_html=True)

        ce, c1, ce, c2, ce = st.columns([0.07, 1, 0.07, 3, 0.07])
        person_name = c1.text_input('按姓名搜索')
        person_id = c1.text_input('按身份证号搜索')
        search = c1.button('搜索')
        if search:
            deta = Deta(st.secrets["deta_key"])
            db_info = deta.Base("person_info")
            db_symptom = deta.Base("person_symptom")
            db_image = deta.Base("imaging")
            db_physical = deta.Base("physical_test")
            db_PMH = deta.Base('PMH')
            person_df = pd.DataFrame(db_info.fetch().items)
            symptom_df = pd.DataFrame(db_symptom.fetch().items)
            imaging_df = pd.DataFrame(db_image.fetch().items)
            pmh_df = pd.DataFrame(db_PMH.fetch().items)
            physicl_df = pd.DataFrame(db_physical.fetch().items)
            print(person_df)
            if person_id != '':
                select_df = person_df[person_df['身份证号'] == person_id]
            else:
                select_df = person_df[person_df['姓名'] == person_name]
                print(select_df)
            # try:
                id = select_df['身份证号'].tolist()[0]
                print(id)
                select_df = select_df.set_index('身份证号')
                print(select_df.loc[id, '姓名'])
                c2.markdown('<p class="label-font">个人基础信息</p>', unsafe_allow_html=True)
                c2.write('患者姓名：%s' % select_df.loc[id, '姓名'])
                c2.write('患者姓别：%s' % select_df.loc[id, '性别'])
                c2.write('联系方式：%s' % select_df.loc[id, '电话'])
                c2.write('身份证：%s' % id)
                c2.markdown('')

                c2.markdown('<p class="label-font">历史症状</p>', unsafe_allow_html=True)
                s_df = symptom_df[symptom_df['身份证号'] == id]
                s_df.drop(columns=['key', '身份证号'], inplace=True)
                c2.table(s_df)

                c2.markdown('<p class="label-font">体格检查</p>', unsafe_allow_html=True)
                ph_df = physicl_df[physicl_df['身份证号'] == id]
                ph_df.drop(columns=['key', '身份证号'], inplace=True)
                print(ph_df)
                c2.table(ph_df)

                c2.markdown('<p class="label-font">影像学检查</p>', unsafe_allow_html=True)
                i_df = imaging_df[imaging_df['身份证号'] == id]
                i_df.drop(columns=['key', '身份证号'], inplace=True)
                c2.table(i_df)

                c2.markdown('<p class="label-font">既往病史</p>', unsafe_allow_html=True)
                p_df = pmh_df[imaging_df['身份证号'] == id]
                p_df.drop(columns=['key', '身份证号'], inplace=True)
                c2.table(p_df)
            # except:
            #     c2.error('未找到患者')