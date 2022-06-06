from hydralit import HydraHeadApp
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from deta import Deta
import datetime


class followupApp(HydraHeadApp):
    def run(self):

        @st.cache(allow_output_mutation=True)
        def get_data_followup():
            return []


        ce, c1, ce, c2, ce, c3, ce = st.columns([0.07, 0.8, 0.07, 0.8, 0.07, 2.4, 0.07])
        person_name = c1.text_input('按姓名搜索')
        person_id = c1.text_input('按身份证号搜索')

        if "questionare_button_clicked" not in st.session_state:
            st.session_state.questionare_button_clicked = False
        if "search_button_clicked" not in st.session_state:
            st.session_state.search_button_clicked = False

        def call_back_questionare():
            st.session_state.questionare_button_clicked = True

        def call_back_search():
            st.session_state.search_button_clicked = True

        if c1.button('搜索患者信息', on_click=call_back_search, key='input') or st.session_state.search_button_clicked:
            deta = Deta(st.secrets["deta_key"])
            db_info = deta.Base("person_info")
            info = pd.DataFrame(db_info.fetch().items)
            if person_id != '':
                select_df = info[info['身份证号'] == person_id]
            else:
                select_df = info[info['姓名'] == person_name]
            try:
                ID = select_df['身份证号'].tolist()[0]
                c2.markdown('<p class="label-font">个人信息</p>', unsafe_allow_html=True)
                select_df = select_df.set_index('身份证号')
                c2.write('患者姓名：%s' % select_df.loc[ID, '姓名'])
                c2.write('患者姓别：%s' % select_df.loc[ID, '性别'])
                c2.write('联系方式：%s' % select_df.loc[ID, '电话'])
                c2.write('身份证号：%s' % ID)
                c2.write('最后随访时间：%s' % select_df.loc[ID, '随访时间'])
                c2.markdown('')

                if c2.button('增加满意度问卷', on_click=call_back_questionare,
                             key='input') or st.session_state.questionare_button_clicked:
                    with c3:
                        c3.markdown('<p class="label-font">满意度问卷</p>', unsafe_allow_html=True)

                        def st_radio_horizontal(*args, **kwargs):
                            st.write(
                                '<style> div[data-testid = column] > div > div > div > div.stRadio > div{flex-direction: row;} </style>',
                                unsafe_allow_html=True)
                            st.write(
                                '<style> div[data-testid = column] > div > div > div > div.stRadio > div > label{padding-right:'
                                '4rem;} </style>',
                                unsafe_allow_html=True)
                            return st.radio(*args, **kwargs)

                        name = locals()
                        question_list = [
                            ['q1', '1. 症状改善是否满意', [['q1_1', '还有什么症状待改善']]],
                            ['q2', '2. 诊疗⽅案是否满意', [['q2_1', '意向采⽤什么⽅案']]],
                            ['q3', '3. 住院费⽤是否满意',
                             [['q3_1', '费⽤是否合理'], ['q3_2', '预期费⽤'], ['q3_3', '有⽆乱收费现象（如：临时加价、变更 计划诊疗⽅案、诱导收费等）']]],
                            ['q4', '4. 住院服务是否满意'],
                            ['q5', '5. 医师服务是否满意', [['q5_1', '医师服务待改进⽅⾯'], ['q5_2', '相关医生']]],
                            ['q6', '6. 护⼠服务是否满意', [['q6_1', '护士服务待改进⽅⾯'], ['q6_2', '相关护士']]],
                            ['q7', '7. 院前服务是否满意', [['q7_1', '服务需改进⽅⾯']]],
                            ['q8', '8. 院前信息系统使⽤是否满意', [['q81', '系统需改进⽅⾯']]],
                            ['q9', '9. 院前问诊是否满意', [['q9_1', '问诊需改进⽅⾯']]],
                            ['q10', '10. 院前分诊/转诊推荐是否满意', [['q10_1', '分诊/转诊推荐需改进⽅⾯']]],
                            ['q11', '11. 院后随诊是否满意', [['q11_1', '希望院后增加服务']]],
                            ['q12', '12. ⽣活指导是否满意', [['q12_1', '希望增加指导内容']]],
                            ['q13', '13. 复诊提醒是否满意', [['q13_1', '希望增加提醒内容']]],
                            ['q14', '14. 药品配送是否满意', [['q14_1', '希望改善配药环节']]]
                        ]
                        for i in question_list:
                            name[i[0]] = st_radio_horizontal(i[1], ('非常不满意', '不满意', '一般', '满意', '非常满意'), index=4)
                            if name[i[0]] != '非常满意' and len(i) == 3:
                                for n in i[2]:
                                    name[n[0]] = st.text_input(n[1])
                        if st.button("提交"):
                            with st.spinner("上传中"):
                                db_followup = deta.Base("followup_info")
                                get_data_followup().clear()
                                for i in question_list:
                                    get_data_followup().append({'问题': i[1], '满意度': name[i[0]]})
                                    if name[i[0]] != '非常满意' and len(i) == 3:
                                        for n in i[2]:
                                            get_data_followup().append({'问题': n[1], '答案': name[n[0]]})
                                    db_followup.put({'key': ID, '满意度问卷': get_data_followup(),
                                                     '数据采集时间': datetime.datetime.now().strftime("%Y-%m-%d")})
                                db_info.update({'随访教育': datetime.datetime.now().strftime("%Y-%m-%d")}, key=ID)
                                st.success('满意度问卷已上传')
                                st.session_state.questionare_button_clicked = False
            except IndexError:
                c2.error('未找到患者')
