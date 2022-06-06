from hydralit import HydraHeadApp
import streamlit as st
import pandas as pd
from deta import Deta
import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from pathlib import Path
import tempfile
from PIL import Image


class medhisApp(HydraHeadApp):
    def run(self):
        @st.cache(allow_output_mutation=True)
        def get_data_medhis():
            return {}

        @st.cache()
        def get_info_data():
            db_info = deta.Base("person_info")
            info = pd.DataFrame(db_info.fetch().items)
            return info

        if "search_button_clicked" not in st.session_state:
            st.session_state.search_button_clicked = False
        if "add_info_button_clicked" not in st.session_state:
            st.session_state.add_info_button_clicked = False

        def call_back_add_info():
            st.session_state.add_info_button_clicked = True

        def call_back_search():
            st.session_state.search_button_clicked = True

        ce, c1, ce, c2, ce, c3, ce = st.columns([0.07, 0.8, 0.07, 1.6, 0.07, 1.6, 0.07])
        person_name = c1.text_input('按姓名搜索')
        person_id = c1.text_input('按身份证号搜索')

        if c1.button('搜索患者信息', on_click=call_back_search, key='input') or st.session_state.search_button_clicked:
            deta = Deta(st.secrets["deta_key"])
            db_info = deta.Base("person_info")
            info = get_info_data()
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
                med_info = deta.Base("medhis_info")
                medhis = med_info.get(ID)
                get_data_medhis().update(medhis['住院信息'])

                with c2:
                    if '出院当日/后⼀日' in get_data_medhis().keys():
                        st.markdown('<p class="label-font">住院信息</p>', unsafe_allow_html=True)
                        st.write('目前状态：出院后')
                        st.write('活动状态：%s' % get_data_medhis()['出院当日/后⼀日']['活动状态'])
                        st.write('入院时间：%s' % get_data_medhis()['⼊院后手术前']['入院时间'])
                        st.write('手术时间：%s' % get_data_medhis()['手术后出院前']['手术时间'])
                        st.write('出院时间：%s' % get_data_medhis()['出院当日/后⼀日']['出院时间'])
                        st.write('预期理疗：%s' % get_data_medhis()['出院当日/后⼀日']['预期理疗'])
                        discharge = c2.button('预览住院小结', key='discharge_view')
                        fee = c2.button('预览费用清单', key='fee_view')
                        if discharge:
                            c3.markdown('<p class="label-font">出院小结</p>', unsafe_allow_html=True)
                            photos = deta.Drive(f'{ID}_discharge'.format(ID=person_id))
                            for value in photos.list().values():
                                res = photos.get(value[0])
                                image = Image.open(res)
                                c3.image(image)
                        if fee:
                            c3.markdown('<p class="label-font">费用清单</p>', unsafe_allow_html=True)
                            photos = deta.Drive(f'{ID}_fee'.format(ID=person_id))
                            for value in photos.list().values():
                                res = photos.get(value[0])
                                image = Image.open(res)
                                c3.image(image)
                    elif '手术后出院前' in get_data_medhis().keys():
                        st.markdown('<p class="label-font">住院信息</p>', unsafe_allow_html=True)
                        st.write('目前状态：手术后出院前')
                        st.write('活动状态：%s' % get_data_medhis()['手术后出院前']['活动状态'])
                        st.write('入院时间：%s' % get_data_medhis()['⼊院后手术前']['入院时间'])
                        st.write('手术时间：%s' % get_data_medhis()['手术后出院前']['手术时间'])
                        st.write('预期出院时间：%s' % get_data_medhis()['手术后出院前']['预期出院时间'])
                        st.write('可能延期原因：%s' % get_data_medhis()['手术后出院前']['可能延期原因'])

                    elif '⼊院后手术前' in get_data_medhis().keys():
                        st.markdown('<p class="label-font">住院信息</p>', unsafe_allow_html=True)
                        st.write('目前状态：⼊院后手术前')
                        st.write('活动状态：%s' % get_data_medhis()['⼊院后手术前']['活动状态'])
                        st.write('入院时间：%s' % get_data_medhis()['⼊院后手术前']['入院时间'])
                        st.write('预期手术时间：%s' % get_data_medhis()['⼊院后手术前']['预期手术时间'])
                    else:
                        pass

                if c2.button('新增住院信息', on_click=call_back_add_info) or st.session_state.add_info_button_clicked:
                    c3.markdown('<p class="label-font">住院信息</p>', unsafe_allow_html=True)
                    his_type = c3.selectbox('时间结点', ('⼊院后手术前', '手术后出院前', '出院当日/后⼀日'), key='his_type')
                    uploaded_discharge = None
                    uploaded_fee = None
                    if his_type == '⼊院后手术前':
                        activity_state = c3.selectbox('活动状态', ('自主活动', '活动受限', '被动活动：轴线翻⾝', '被动活动：下肢抬⾼'),
                                                      key='his_type')
                        inpatient_time = c3.date_input('入院时间', datetime.date(2022, 5, 26), key='inpatient_time')
                        surgery_time = c3.date_input('预期手术时间', datetime.date(2022, 5, 26), key='surgery_time')
                    elif his_type == '手术后出院前':
                        activity_state = c3.selectbox('活动状态', ('自主活动', '活动受限', '被动活动：轴线翻⾝', '被动活动：下肢抬⾼'),
                                                      key='his_type')
                        surgery_time = c3.date_input('手术时间', datetime.date(2022, 5, 26), key='surgery_time')
                        discharge_time = c3.date_input('预计出院时间', datetime.date(2022, 5, 26), key='discharge_time')
                        extention_reson = c3.selectbox('是否有以下症状', ('无以下症状', '发热', '血尿', '手术部位感染', '腰部疼痛无缓解或者加剧'))
                    else:
                        activity_state = c3.selectbox('活动状态', ('自主活动', '活动受限', '被动活动：轴线翻⾝', '被动活动：下肢抬⾼'),
                                                      key='his_type')
                        physical = c3.selectbox('理疗需求', ('不需要', '运动疗法', '康复训练', '牵引治疗'),
                                                key='physical')
                        discharge_time = c3.date_input('出院时间', datetime.date(2022, 5, 26), key='discharge_time')
                        uploaded_discharge = c3.file_uploader("请上传出院小结", accept_multiple_files=True)
                        uploaded_fee = c3.file_uploader("请上传发票扫描件", accept_multiple_files=True)

                    if c3.button('增加'):
                        if uploaded_discharge:
                            for i in uploaded_discharge:
                                with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                                    fp = Path(tmp_file.name)
                                    fp.write_bytes(i.getvalue())
                                photos = deta.Drive(f'{ID}_discharge'.format(ID=person_id))
                                photos.put(i.name, path=fp)
                        else:
                            c3.error('请上传出院小结')
                            st.stop()
                        if uploaded_fee:
                            for i in uploaded_fee:
                                with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                                    fp = Path(tmp_file.name)
                                    fp.write_bytes(i.getvalue())
                                photos = deta.Drive(f'{ID}_fee'.format(ID=person_id))
                                photos.put(i.name, path=fp)
                        else:
                            c3.error('请上传费用清单')
                            st.stop()
                        if his_type == '⼊院后手术前':
                            get_data_medhis().update({his_type: {'活动状态': activity_state,
                                                                 '入院时间': inpatient_time.strftime("%Y-%m-%d"),
                                                                 '预期手术时间': surgery_time.strftime("%Y-%m-%d")}})
                        elif his_type == '手术后出院前':
                            get_data_medhis().update({his_type: {'活动状态': activity_state,
                                                                 '手术时间': surgery_time.strftime("%Y-%m-%d"),
                                                                 '预期出院时间': discharge_time.strftime("%Y-%m-%d"),
                                                                 '可能延期原因': extention_reson}})
                        else:
                            get_data_medhis().update({his_type: {'活动状态': activity_state, '预期理疗': physical,
                                                      '出院时间': discharge_time.strftime("%Y-%m-%d")}})
                        db_medhis = deta.Base("medhis_info")
                        db_info.update({'住院记录': datetime.datetime.now().strftime("%Y-%m-%d")}, key=ID)
                        db_medhis.put({'key': ID, '住院信息': get_data_medhis(),
                                       '数据采集时间': datetime.datetime.now().strftime("%Y-%m-%d")})
                        st.session_state.add_info_button_clicked = False
                        st.experimental_rerun()

            except IndexError:
                st.error('不存在患者信息，请进行院前信息填报流程')
