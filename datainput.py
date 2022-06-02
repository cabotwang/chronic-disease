import streamlit as st
import pandas as pd
from hydralit import HydraHeadApp
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from hydralit_components import HyLoader, Loaders
import datetime
from deta import Deta


class datainputApp(HydraHeadApp):
    def run(self):
        global id

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

        deta = Deta(st.secrets["deta_key"])
        db_info = deta.Base("person_info")
        details_info = deta.Base("details_info")

        @st.cache(allow_output_mutation=True)
        def get_data_sym():
            return []

        @st.cache(allow_output_mutation=True)
        def get_data_ph():
            return []

        @st.cache(allow_output_mutation=True)
        def get_data_image():
            return []

        @st.cache(allow_output_mutation=True)
        def get_data_pmh():
            return []

        # 个人基础信息
        with st.container():
            st.markdown('<p class="label-font">个人基础信息</p>', unsafe_allow_html=True)
            c1, ce, c2, ce, c3, ce, c4 = st.columns([1, 0.07, 1, 0.07, 1.5, 0.07, 2])
            name = c1.text_input('姓名', max_chars=12)
            sex = c2.selectbox('性别', ('男', '女', '其他'))
            phone = c3.text_input('联系方式', max_chars=11)
            id = c4.text_input('身份证号码', max_chars=18)
            ideal_area = c1.selectbox('倾向治疗区域', ('无倾向', '本市', '外市'), key='ideal_area')
            ideal_therapy = c2.selectbox('倾向治疗方式', ('无倾向', '保守', '微创手术', '开放手术'), key='ideal_therapy')
            search = c1.button('搜索', help='根据身份证号进行搜索')
            if search:
                info = pd.DataFrame(db_info.fetch().items)
                if id in info["身份证号"].tolist():
                    st.info('存在患者信息,已经同步')
                    details = details_info.get(id)

                    for i in [['症状体征', get_data_sym()], ['体格检查', get_data_ph()], ['影像学检查', get_data_image()],
                              ['既往病史', get_data_pmh()]]:
                        i[1].clear()
                        i[1].extend(details[i[0]])
                else:
                    st.info('不存在患者信息')
        st.markdown('')

        # 症状体征
        with st.container():
            option1 = []
            st.markdown('<p class="label-font">症状体征</p>', unsafe_allow_html=True)
            options = st.multiselect('您是否患有以下症状（可多选）', ('腰痛', '神经根性疼痛', '下肢麻木无力', '⼤⼩便功能障碍', '其他：'))
            st.write()
            if options:
                with st.expander('详细信息', expanded=True):
                    names = locals()
                    if '其他：' in options:
                        st.markdown('<p class="label-font2">其他</p>', unsafe_allow_html=True)
                        c1, ce, c2, ce, c3 = st.columns([1, 0.07, 1, 0.07, 1])
                        name = c1.text_input('症状名称', key='other')
                        degree = c2.selectbox('程度', ('轻', '中', '重'), key='degree')
                        paintype = c3.selectbox('类型', ('持续', '间断'), index=1, key='other')
                        if paintype == '间断':
                            duration = c1.text_input('平均发作时长（小时）', key='duration', help='可填写单一数值，如为范围区间，可用“-”相隔')
                            incidence = c2.text_input('发作频次（次/周）', key='incidence')
                        else:
                            chronic_pain_time = c1.text_input('持续时间（周）', key='other')
                    for i in options:
                        if i != '其他：':
                            option1.append(i)
                    counter = 0
                    for each in option1:
                        st.markdown('<p class="label-font2">%s</p>' % each, unsafe_allow_html=True)
                        c1, ce, c2, ce, c3 = st.columns([1, 0.07, 1, 0.07, 1])
                        names['%s_degree' % counter] = c1.selectbox('程度', ('轻', '中', '重'), key='%sdegree' % each)
                        names['%s_type' % counter] = c2.selectbox('类型', ('持续', '间断'), key=each)
                        if names['%s_type' % counter] == '间断':
                            names['%s_duration' % counter] = c3.text_input('平均发作时长（小时）', key='%s_duration' % each,
                                                                           help='可填写单一数值，如为范围区间，可用“-”相隔')
                            names['%s_incidence' % counter] = c1.text_input('发作频次（次/周）', key='%s_incidence' % each)
                        else:
                            names['%s_chronicpaintime' % counter] = c3.text_input('持续时间（周）', key=each)
                            counter += 1
                    submit_physical = st.button('确认')
                    if submit_physical:
                        if '其他：' in options:
                            try:
                                get_data_sym().append({'症状': name, '程度': degree, '类型': paintype,
                                                       '平均发作时长（小时）': duration, '发作频次（次/周）': incidence,
                                                       '录入时间': datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")})
                            except UnboundLocalError:
                                get_data_sym().append(
                                    {'症状': name, '程度': degree, '类型': paintype, '持续时间（周）': chronic_pain_time,
                                     '录入时间': datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")})
                        counter = 0
                        for each in option1:
                            try:
                                get_data_sym().append(
                                    {'症状': each, '程度': names['%s_degree' % counter], '类型': names['%s_type' % counter],
                                     '平均发作时长（小时）': names['%s_duration' % counter],
                                     '发作频次（次/周）': names['%s_incidence' % counter],
                                     '录入时间': datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")})
                            except:
                                get_data_sym().append(
                                    {'症状': each, '程度': names['%s_degree' % counter], '类型': names['%s_type' % counter],
                                     '持续时间（周）': names['%s_chronicpaintime' % counter],
                                     '录入时间': datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")})
                            counter += 1
                        st.experimental_rerun()

            df = pd.DataFrame(get_data_sym(), columns=['症状', '程度', '类型', '持续时间（周）', '平均发作时长（小时）',
                                                       '发作频次（次/周）', '录入时间'])
            df.index = df.index + 1
            df = df.where(df.notnull(), '')
            if len(df) > 0:
                selected = interactive_table(df)
                c1, ce, c2, ce = st.columns([1, 0.07, 1, 10])
                delete = c1.button('删除所选信息', key='symptom_delete')
                clear = c2.button('清除列表', key='symptom_clear')
                if delete:
                    print(get_data_sym())
                    print(selected["selected_rows"][0])
                    for i in get_data_sym():
                        if set(i.items()).issubset(selected["selected_rows"][0].items()):
                            get_data_sym().remove(i)
                    st.experimental_rerun()
                if clear:
                    get_data_sym().clear()
                    st.experimental_rerun()
        st.markdown('')

        # 体格检查
        with st.container():
            st.markdown('<p class="label-font">体格检查</p>', unsafe_allow_html=True)
            my_form = st.expander('增加体格检查结果')
            c1, ce, c2, ce, c3 = my_form.columns([1, 0.07, 1, 0.07, 1])
            physics = c1.selectbox('体格检查类型', ('直腿抬⾼试验', '直腿抬⾼加强试验', '健侧直腿抬⾼试验', '股神经牵拉试验', '腱反射较健侧减弱',
                                              '其他'), key='physics_name')
            if physics != '其他':
                physics_time = c2.date_input('检查时间', datetime.date(2022, 5, 26), key='ph_time')
                physics_result = c3.selectbox('检查结果', ('阳性', '阴性'), key='result')
            else:
                physics = c2.text_input('请输入体格检查名称', key='special_ph')
                physics_time = c3.date_input('检查时间', datetime.date(2022, 5, 26), key='ph_time')
                physics_result = c1.selectbox('检查结果', ('阳性', '阴性'), key='result')
            submit_image = c1.button('增加', key='physics')
            if submit_image:
                get_data_ph().append({'检查类型': physics, '日期': physics_time.strftime('%Y-%m-%d'), '检查结果': physics_result,
                                      '录入时间': datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")})
                st.experimental_rerun()

            df = pd.DataFrame(get_data_ph(), columns=['检查类型', '日期', '检查结果', '录入时间'])
            df = df.where(df.notnull(), '')
            df.index = df.index + 1
            if len(df) > 0:
                selected = interactive_table(df)
                c1, ce, c2, ce = st.columns([1, 0.07, 1, 10])
                delete = c1.button('删除所选信息', key='physics_delete')
                clear = c2.button('清除列表', key='physics_clear')
                if delete:
                    get_data_ph().remove(selected["selected_rows"][0])
                    st.experimental_rerun()
                if clear:
                    get_data_ph().clear()
                    st.experimental_rerun()
        st.markdown('')

        # 影像学检查
        with st.container():
            st.markdown('<p class="label-font">影像学检查</p>', unsafe_allow_html=True)
            my_form = st.expander('增加影像学检查结果')
            c1, ce, c2, ce, c3, ce = my_form.columns([1, 0.07, 1, 0.07, 1, 0.07])
            image = c1.selectbox('影像学检查类型', ('X光', 'CT', 'MRI', '其他'), key='image_name')
            if image != '其他':
                image_time = c2.date_input('最近一次检查时间', datetime.date(2022, 5, 26), key='time')
                result = c3.multiselect('检查结果', ('腰椎间盘退变,损伤', '椎间盘局限性突出', '压迫神经根,⻢尾'), key='result')
            else:
                image = c2.text_input('请输入影像学检查名称', key='special_image')
                image_time = c3.date_input('最近一次检查时间', datetime.date(2022, 5, 26), key='time')
                result = c1.multiselect('检查结果', ('腰椎间盘退变,损伤', '椎间盘局限性突出', '压迫神经根,⻢尾'), key='result')
            submit_image = c1.button('增加')
            if submit_image:
                get_data_image().append(
                    {'检查类型': image, '日期': image_time.strftime('%Y-%m-%d'), '检查结果': ' / '.join(result),
                     '录入时间': datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")})
                st.experimental_rerun()

            df = pd.DataFrame(get_data_image(), columns=['检查类型', '日期', '检查结果', '录入时间'])
            df = df.where(df.notnull(), '')
            df.index = df.index + 1
            if len(df) > 0:
                selected = interactive_table(df)
                c1, ce, c2, ce = st.columns([1, 0.07, 1, 10])
                delete = c1.button('删除所选信息', key='image_delete')
                clear = c2.button('清除列表', key='image_clear')
                if delete:
                    get_data_image().remove(selected["selected_rows"][0])
                    st.experimental_rerun()
                if clear:
                    get_data_image().clear()
                    st.experimental_rerun()
        st.markdown('')

        # 既往病史
        with st.container():
            st.markdown('<p class="label-font">既往病史</p>', unsafe_allow_html=True)
            my_form = st.expander('增加既往症信息')
            c1, ce, c2, ce, c3 = my_form.columns([1, 0.07, 1, 0.07, 1])
            dn = c1.selectbox('既往诊断', ('腰椎间盘突出症', '其他'), key='name')
            if dn == '其他':
                dn = c2.text_input('既往诊断名称', key='special_name')
                dn_time = c3.text_input('患病时长（年）', key='time')
                tm = c1.multiselect('治疗方式', ('保守-药物', '保守-理疗', '⼿术-微创', '⼿术-开放'))
            else:
                dn_time = c2.text_input('患病时长（年）', key='time')
                tm = c3.multiselect('治疗方式', ('保守-药物', '保守-理疗', '⼿术-微创', '⼿术-开放'))

            if '保守-药物' in tm:
                my_form.markdown('<p class="label-font2">保守-药物</p>', unsafe_allow_html=True)
                c1, ce, c2, ce, c3 = my_form.columns([1, 0.07, 1, 0.07, 1])
                drug_name = c1.text_input('药品名称', key='drug_name')
                drug_use = c2.text_input('用法用量', key='drug_use', help='需填写剂量、单位、应用频次、给药途径，如：600 mg，三次每日，口服')
                drug_start = c3.date_input('开始时间', datetime.date(2022, 5, 26), key='durg_time')
                drug_dur = c1.text_input('疗程', key='drug_dur')
                drug_effect = c2.selectbox('药物效果', ('症状缓解', '症状稍缓解', '症状未缓解', '其他'), key='drug_effect')
                if drug_effect == '其他':
                    drug_effect = c3.text_input('请说明', key='drug_effect_other')
                    drug_hospital = c1.text_input('就诊医疗机构', key='drug_hospital')
                else:
                    drug_hospital = c3.text_input('就诊医疗机构', key='drug_hospital')

            if '保守-理疗' in tm:
                my_form.markdown('<p class="label-font2">保守-理疗</p>', unsafe_allow_html=True)
                c1, ce, c2, ce, c3 = my_form.columns([1, 0.07, 1, 0.07, 1])
                therapy_name = c1.selectbox('理疗项目', ('运动疗法', '康复训练', '牵引治疗', '矫形器装配体外冲击波治疗', '电刺激疗法',
                                                     '激光治疗', '针灸治疗', '推拿按摩', '拔罐治疗', '刮痧治疗', '其他'), key='therapy_name')
                if therapy_name != '其他':
                    therapy_time = c2.date_input('治疗时间', datetime.date(2022, 5, 26), key='therapy_time')
                    therapy_dur = c3.text_input('疗程', key='therapy_dur')
                    therapy_effect = c1.selectbox('理疗效果', ('症状缓解', '症状稍缓解', '症状未缓解', '其他'), key='therapy_effect')
                    if therapy_effect == '其他':
                        therapy_effect = c2.text_input('请说明', key='therapy_effect_other')
                        therapy_hospital = c3.text_input('就诊医疗机构', key='therapy_hospital')
                    else:
                        therapy_hospital = c2.text_input('就诊医疗机构', key='therapy_hospital')
                else:
                    therapy_name = c2.text_input('请具体说明', key='spe_surgery_effect')
                    therapy_time = c3.date_input('治疗时间', datetime.date(2022, 5, 26), key='therapy_time')
                    therapy_dur = c1.text_input('疗程', key='therapy_dur')
                    therapy_effect = c2.selectbox('理疗效果', ('症状缓解', '症状稍缓解', '症状未缓解', '其他'), key='therapy_effect')
                    if therapy_effect == '其他':
                        therapy_effect = c3.text_input('请说明', key='therapy_effect_other')
                        therapy_hospital = c1.text_input('就诊医疗机构', key='therapy_hospital')
                    else:
                        therapy_hospital = c3.text_input('就诊医疗机构', key='therapy_hospital')

            if '⼿术-开放' in tm:
                my_form.markdown('<p class="label-font2">⼿术-开放</p>', unsafe_allow_html=True)
                c1, ce, c2, ce, c3 = my_form.columns([1, 0.07, 1, 0.07, 1])
                surgery_name = c1.selectbox('术式', ('腰椎融合术', '腰椎人工椎间盘置换术', '其他'), key='surgery_name')
                if surgery_name != '其他':
                    surgery_time = c2.date_input('手术时间', datetime.date(2022, 5, 26), key='surgery_time')
                    surgery_effect = c3.selectbox('手术效果', ('症状缓解', '症状稍缓解', '症状未缓解', '其他'), key='surgery_effect')
                    if surgery_effect == '其他':
                        surgery_effect = c1.text_input('请说明', key='surgery_effect_other')
                        surgery_hospital = c2.text_input('就诊医疗机构', key='surgery_hospital')
                    else:
                        surgery_hospital = c1.text_input('就诊医疗机构', key='surgery_hospital')
                else:
                    surgery_name = c2.text_input('请具体说明', key='spe_surgery_effect')
                    surgery_time = c3.date_input('手术时间', datetime.date(2022, 5, 26), key='surgery_time')
                    surgery_effect = c1.selectbox('手术效果', ('症状缓解', '症状稍缓解', '症状未缓解', '其他'), key='surgery_effect')
                    if surgery_effect == '其他':
                        surgery_effect = c2.text_input('请说明', key='surgery_effect_other')
                        surgery_hospital = c3.text_input('就诊医疗机构', key='surgery_hospital')
                    else:
                        surgery_hospital = c2.text_input('就诊医疗机构', key='surgery_hospital')

            if '⼿术-微创' in tm:
                my_form.markdown('<p class="label-font2">⼿术-微创</p>', unsafe_allow_html=True)
                c1, ce, c2, ce, c3 = my_form.columns([1, 0.07, 1, 0.07, 1])
                microsurgery_name = c1.selectbox('术式', ('经皮椎间盘切吸术', '经皮椎间盘激光消融术', '经皮椎间盘臭氧消融术及射频消融髓核成形术',
                                                        '经皮椎间盘等离子消融术', '经皮椎间盘胶原酶化学溶解术', '显微腰椎间盘切除术',
                                                        '显微内窥镜腰椎间盘切除术', '经皮内镜腰椎间盘切除术', '椎间盘髓核摘除术', '其他'),
                                                 key='microsurgery_name')
                if microsurgery_name != '其他':
                    microsurgery_time = c2.date_input('手术时间', datetime.date(2022, 5, 26), key='microsurgery_time')
                    microsurgery_effect = c3.selectbox('手术效果', ('症状缓解', '症状稍缓解', '症状未缓解', '其他'),
                                                       key='microsurgery_effect')
                    if microsurgery_effect == '其他':
                        microsurgery_effect = c1.text_input('请说明', key='microsurgery_effect_other')
                        microsurgery_hospital = c2.text_input('就诊医疗机构', key='microsurgery_hospital')
                    else:
                        microsurgery_hospital = c1.text_input('就诊医疗机构', key='microsurgery_hospital')
                else:
                    microsurgery_name = c2.text_input('请具体说明', key='spe_surgery_effect')
                    microsurgery_time = c3.date_input('手术时间', datetime.date(2022, 5, 26), key='microsurgery_time')
                    microsurgery_effect = c1.selectbox('手术效果', ('症状缓解', '症状稍缓解', '症状未缓解', '其他'),
                                                       key='microsurgery_effect')
                    if microsurgery_effect == '其他':
                        microsurgery_effect = c2.text_input('请说明', key='microsurgery_effect_other')
                        microsurgery_hospital = c3.text_input('就诊医疗机构', key='microsurgery_hospital')
                    else:
                        microsurgery_hospital = c2.text_input('就诊医疗机构', key='microsurgery_hospital')

            submit_image = my_form.button('增加', key='phm')
            if submit_image:
                for i in tm:
                    if i == '保守-药物':
                        get_data_pmh().append({'既往诊断': dn, '患病时长（年）': dn_time, '治疗方式': i, '名称': drug_name,
                                               '用法用量': drug_use, '时间': drug_start.strftime('%Y-%m-%d'), '疗程': drug_dur,
                                               '效果': drug_effect, '医疗机构': drug_hospital,
                                               '录入时间': datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")})
                    if i == '保守-理疗':
                        get_data_pmh().append({'既往诊断': dn, '患病时长（年）': dn_time, '治疗方式': i, '名称': therapy_name,
                                               '时间': therapy_time.strftime('%Y-%m-%d'), '疗程': therapy_dur,
                                               '效果': therapy_effect, '医疗机构': therapy_hospital,
                                               '录入时间': datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")})
                    if i == '⼿术-开放':
                        get_data_pmh().append({'既往诊断': dn, '患病时长（年）': dn_time, '治疗方式': i, '名称': surgery_name,
                                               '时间': surgery_time.strftime('%Y-%m-%d'), '效果': surgery_effect,
                                               '医疗机构': surgery_hospital,
                                               '录入时间': datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")})
                    if i == '⼿术-微创':
                        get_data_pmh().append({'既往诊断': dn, '患病时长（年）': dn_time, '治疗方式': i, '名称': microsurgery_name,
                                               '时间': microsurgery_time.strftime('%Y-%m-%d'), '效果': microsurgery_effect,
                                               '医疗机构': microsurgery_hospital,
                                               '录入时间': datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")})
                st.experimental_rerun()
            df = pd.DataFrame(get_data_pmh(), columns=['既往诊断', '患病时长（年）', '治疗方式', '名称', '时间', '疗程', '效果',
                                                       '医疗机构', '用法用量', '录入时间'])
            df = df.where(df.notnull(), '')
            df.index = df.index + 1

            if len(df) > 0:
                selected = interactive_table(df)
                c1, ce, c2, ce = st.columns([1, 0.07, 1, 10])
                delete = c1.button('删除所选信息', key='pmh_delete')
                clear = c2.button('清除列表', key='pmh_clear')
                if delete:
                    for i in get_data_pmh():
                        if set(i.items()).issubset(selected["selected_rows"][0].items()):
                            get_data_pmh().remove(i)
                    st.experimental_rerun()
                if clear:
                    get_data_pmh().clear()
                    st.experimental_rerun()
        st.markdown('')

        final_submit = st.button('提交')
        if final_submit:
            if '' in [name, sex, phone]:
                st.error('无法提交：基础信息不完整')
            else:
                with st.spinner("上传中"):
                    db_details = deta.Base("details_info")
                    db_info.update({"姓名": name, '性别': sex, '电话': phone, "身份证号": id, '倾向治疗区域': ideal_area,
                                    '倾向治疗方式': ideal_therapy,
                                    '数据采集': datetime.datetime.now().strftime("%Y-%m-%d")}, id)
                    db_details.put({'key': id, '症状体征': get_data_sym(), '影像学检查': get_data_image(),
                                    '既往病史': get_data_pmh(), '体格检查': get_data_ph()})
                    get_data_sym().clear()
                    get_data_image().clear()
                    get_data_pmh().clear()
                    get_data_ph().clear()
                    st.success('上传成功')
