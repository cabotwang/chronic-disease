import streamlit as st
import pandas as pd
from hydralit import HydraHeadApp
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import datetime


class datainputApp(HydraHeadApp):
    def run(self):

        def interactive_table(df: pd.DataFrame):
            builder = GridOptionsBuilder.from_dataframe(df, enableRowGroup=True, enableValue=True, enablePivot=True)
            builder.configure_selection("single")
            selection = AgGrid(
                df,
                enable_enterprise_modules=True,
                gridOptions=builder.build(),
                fit_columns_on_grid_load=True,
                enablePivot=True,
                height=200,
                theme='light',
                update_mode=GridUpdateMode.MODEL_CHANGED,
                allow_unsafe_jscode=True,
            )
            return selection

        st.markdown("""
        <style>
        .label-font {
            font-size:20px; font:sans serif; font-weight:700; 
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("""
        <style>
        .label-font2 {
            font-size:16px; font:sans serif; font-weight:700;
        }
        </style>
        """, unsafe_allow_html=True)

        # 个人基础信息
        with st.container():
            st.markdown('<p class="label-font">个人基础信息</p>', unsafe_allow_html=True)
            ce, c1, ce, c2, ce, c3, ce, c4, ce = st.columns([0.07, 1, 0.07, 1, 0.07, 2.5, 0.07, 3, 0.07])
            name = c1.text_input('姓名')
            sex = c2.selectbox('性别', ('男', '女', '其他'))
            phone = c3.text_input('联系方式')
            id = c4.text_input('身份证号码')
        st.markdown('')

        # 症状体征
        with st.container():
            @st.cache(allow_output_mutation=True)
            def get_data():
                return []

            option1 = []
            st.markdown('<p class="label-font">症状体征</p>', unsafe_allow_html=True)
            ce, c1, ce = st.columns([0.01, 1.1, 0.01])
            options = c1.multiselect('您是否患有以下症状（可多选）', ('腰痛', '神经根性疼痛', '下肢⿇⽊⽆⼒', '⼤⼩便功能障碍', '其他：'))
            if options:
                with st.expander('详细信息', expanded=True):
                    if '其他：' in options:
                        st.markdown('<p class="label-font2">其他</p>', unsafe_allow_html=True)
                        ce, c1, ce, c2, ce, c3, ce = st.columns([0.02, 1, 0.07, 1, 0.07, 1, 0.07])
                        name = c1.text_input('症状名称', key='other')
                        degree = c2.selectbox('程度', ('轻', '中', '重'), key='degree')
                        paintype = c3.selectbox('类型', ('间断', '持续'), key='other')
                        time = c1.text_input('持续时间（小时）', key='other')
                    for i in options:
                        if i != '其他：':
                            option1.append(i)
                    for each in option1:
                        st.markdown('<p class="label-font2">%s</p>' % each, unsafe_allow_html=True)
                        ce, c1, ce, c2, ce, c3, ce = st.columns([0.02, 1, 0.07, 1, 0.07, 1, 0.07])
                        degree = c1.selectbox('程度', ('轻', '中', '重'), key='%sdegree' % each)
                        paintype = c2.selectbox('类型', ('间断', '持续'), key=each)
                        time = c3.text_input('持续时间（小时）', key=each)
                    submit_physical = st.button('确认')
                    if submit_physical:
                        if '其他：' in options:
                            get_data().append({'症状': name, '程度': degree, '类型': paintype, '持续时间（周）': time,
                                               '录入时间': datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")})
                        for each in option1:
                            get_data().append({'症状': each, '程度': degree, '类型': paintype, '持续时间（周）': time,
                                               '录入时间': datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")})
                    df = pd.DataFrame(get_data())
                    df.index = df.index + 1
                if len(df) > 0:
                    selected = interactive_table(df)
                    c1, ce, c2, ce = st.columns([1, 0.07, 1, 10])
                    delete = c1.button('删除所选信息', key='symptom_delete')
                    clear = c2.button('清除列表', key='symptom_clear')
                    if delete:
                        get_data().remove(selected["selected_rows"][0])
                        st.experimental_rerun()
                    if clear:
                        get_data().clear()
                        st.experimental_rerun()
        st.markdown('')

        with st.container():
            st.markdown('<p class="label-font">体格检查</p>', unsafe_allow_html=True)
            st.write('是否进行以下体格检查')
            ce, c1, ce, c2, ce, c3, ce, c4, ce, c5, ce = st.columns([0.07, 1, 0.07, 1, 0.07, 1, 0.07, 1, 0.07, 1, 0.07])
            task1 = c1.selectbox('直腿抬⾼试验', ('未进行', '阳性', '阴性'), key='1')
            task2 = c2.selectbox('直腿抬⾼加强试验', ('未进行', '阳性', '阴性'), key='2')
            task3 = c3.selectbox('健侧直腿抬⾼试验', ('未进行', '阳性', '阴性'), key='3')
            task4 = c4.selectbox('股神经牵拉试验', ('未进行', '阳性', '阴性'), key='4')
            task5 = c5.selectbox('腱反射较健侧减弱', ('未进行', '阳性', '阴性'), key='5')
        st.markdown('')

        with st.container():
            @st.cache(allow_output_mutation=True)
            def get_data1():
                return []

            st.markdown('<p class="label-font">影像学检查</p>', unsafe_allow_html=True)
            my_form = st.expander('增加影像学检查结果')
            c1, ce, c2, ce, c3, ce = my_form.columns([1, 0.07, 1, 0.07, 1, 0.07])
            image = c1.selectbox('影像学检查类型', ('X光', 'CT', 'MRI'), key='name')
            image_time = c2.date_input('最近一次检查时间', datetime.date(2022, 5, 26), key='time')
            result = c3.multiselect('检查结果', ('腰椎间盘退变、损伤', '椎间盘局限性突出', '压迫神经根、⻢尾'), key='result')
            submit_image = c1.button('增加')
            if submit_image:
                get_data1().append({'检查类型': image, '日期': image_time.strftime('%Y-%m-%d'), '检查结果': ' / '.join(result),
                                    '录入时间': datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")})

            df = pd.DataFrame(get_data1(), columns=['检查类型', '日期', '检查结果', '录入时间'])
            df.index = df.index + 1
            if len(df) > 0:
                selected = interactive_table(df)
                c1, ce, c2, ce = st.columns([1, 0.07, 1, 10])
                delete = c1.button('删除所选信息', key='image_delete')
                clear = c2.button('清除列表', key='image_clear')
                if delete:
                    get_data1().remove(selected["selected_rows"][0])
                    st.experimental_rerun()
                if clear:
                    get_data1().clear()
                    st.experimental_rerun()


        with st.container():
            @st.cache(allow_output_mutation=True)
            def get_data2():
                return []

            st.markdown('<p class="label-font">既往病史</p>', unsafe_allow_html=True)
            my_form = st.expander('增加既往症信息')
            c1, ce, c2, ce, c3, ce = my_form.columns([1, 0.07, 1, 0.07, 1, 0.07])
            dn = c1.text_input('既往诊断', key='name')
            dn_time = c2.text_input('患病时长', key='time')
            tm = c3.multiselect('治疗方式', ('保守-药物', '保守-理疗', '⼿术-微创', '⼿术-开放'))

            if '保守-药物' in tm:
                my_form.markdown('<p class="label-font2">保守-药物</p>', unsafe_allow_html=True)
                c1, ce, c2, ce, c3, ce = my_form.columns([1, 0.07, 1, 0.07, 1, 0.07])
                drug_name = c1.text_input('药品名称', key='drug_name')
                drug_use = c2.text_input('用法用量', key='drug_use')
                drug_start = c3.date_input('开始时间', datetime.date(2022, 5, 26), key='durg_time')
                drug_dur = c1.text_input('疗程', key='drug_dur')
                drug_other = c2.text_input('药物效果', key='drug_effect')

            if '保守-理疗' in tm:
                my_form.markdown('<p class="label-font2">保守-理疗</p>', unsafe_allow_html=True)
                c1, ce, c2, ce, c3, ce = my_form.columns([1, 0.07, 1, 0.07, 1, 0.07])
                therapy_name = c1.text_input('理疗项目', key='therapy_name')
                therapy_time = c2.date_input('手术时间', datetime.date(2022, 5, 26), key='therapy_time')
                therapy_dur = c3.text_input('疗程', key='therapy_dur')
                therapy_effect = c1.text_input('理疗效果', key='therapy_effect')

            if '⼿术-开放' in tm:
                my_form.markdown('<p class="label-font2">⼿术-开放</p>', unsafe_allow_html=True)
                c1, ce, c2, ce, c3, ce = my_form.columns([1, 0.07, 1, 0.07, 1, 0.07])
                surgery_name = c1.text_input('术式', key='surgery_name')
                surgery_time = c2.date_input('手术时间', datetime.date(2022, 5, 26), key='surgery_time')
                surgery_effect = c3.text_input('手术效果', key='surgery_effect')

            if '⼿术-微创' in tm:
                my_form.markdown('<p class="label-font2">⼿术-微创</p>', unsafe_allow_html=True)
                c1, ce, c2, ce, c3, ce = my_form.columns([1, 0.07, 1, 0.07, 1, 0.07])
                microsurgery_name = c1.text_input('术式', key='surgery_name')
                microsurgery_time = c2.date_input('手术时间', datetime.date(2022, 5, 26), key='surgery_time')
                microsurgery_effect = c3.text_input('手术效果', key='surgery_effect')

            submit_image = my_form.button('增加', key='phm')
            if submit_image:
                for i in tm:
                    if i == '保守-药物':
                        get_data2().append({'既往诊断': dn, '患病时长（年）': dn_time, '治疗方式': i, '名称': drug_name,
                                            '用法用量': drug_use, '时间': drug_start.strftime('%Y-%m-%d'), '疗程': drug_dur,
                                            '效果': drug_other,
                                            '录入时间': datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")})
                    if i == '保守-理疗':
                        get_data2().append({'既往诊断': dn, '患病时长（年）': dn_time, '治疗方式': i, '名称': therapy_name,
                                            '时间': therapy_time.strftime('%Y-%m-%d'), '疗程': therapy_dur,
                                            '效果': therapy_effect,
                                            '录入时间': datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")})
                    if i == '⼿术-开放':
                        get_data2().append({'既往诊断': dn, '患病时长（年）': dn_time, '治疗方式': i, '名称': surgery_name,
                                            '时间': surgery_time.strftime('%Y-%m-%d'), '效果': surgery_effect,
                                            '录入时间': datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")})
                    if i == '⼿术-微创':
                        get_data2().append({'既往诊断': dn, '患病时长（年）': dn_time, '治疗方式': i, '名称': microsurgery_name,
                                            '时间': microsurgery_time.strftime('%Y-%m-%d'), '效果': microsurgery_effect,
                                            '录入时间': datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")})
                        st.experimental_rerun()
            df = pd.DataFrame(get_data2())
            df = df.where(df.notnull(), '')
            df.index = df.index + 1

            if len(df) > 0:
                selected = interactive_table(df)
                c1, ce, c2, ce = st.columns([1, 0.07, 1, 10])
                delete = c1.button('删除所选信息', key='pmh_delete')
                clear = c2.button('清除列表', key='pmh_clear')
                if delete:
                    get_data2().remove(selected["selected_rows"][0])
                    st.experimental_rerun()
                if clear:
                    get_data2().clear()
                    st.experimental_rerun()

        final_submit = st.button('提交')
