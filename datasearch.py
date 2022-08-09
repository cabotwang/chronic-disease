import streamlit as st
import pandas as pd
from hydralit import HydraHeadApp
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from deta import Deta
import datetime
import hydralit_components as hc
from recommend import phy_recommend

class datasearchApp(HydraHeadApp):
    def run(self):

        def show_table(df: pd.DataFrame):
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

        ce, c1, ce, c2, c3, ce = st.columns([0.07, 0.8, 0.07, 1, 1.6, 0.07])
        person_name = c1.text_input('按姓名搜索')
        person_id = c1.text_input('按身份证号搜索')
        search = c1.button('搜索')
        if search:
            t1 = datetime.datetime.now()
            deta = Deta(st.secrets["deta_key"])
            db_info = deta.Base("person_info")
            db_details = deta.Base("details_info")
            db_followup = deta.Base("followup_info")
            person_df = pd.DataFrame(db_info.fetch().items)

            if person_id != '':
                select_df = person_df[person_df['身份证号'] == person_id]
            else:
                select_df = person_df[person_df['姓名'] == person_name]
            try:
                id = select_df['身份证号'].tolist()[0]
                details = db_details.get(id)
                select_df = select_df.set_index('身份证号')
                print(select_df)
                c2.subheader('患者信息')
                c2.markdown('<p class="label-font">个人基础信息</p>', unsafe_allow_html=True)
                c2.write('患者姓名：%s' % select_df.loc[id, '姓名'])
                c2.write('患者姓别：%s' % select_df.loc[id, '性别'])
                c2.write('联系方式：%s' % select_df.loc[id, '电话'])
                c2.write('身份证号：%s' % id)
                c2.write('倾向治疗区域：%s' % select_df.loc[id, '倾向治疗区域'])
                c2.write('倾向治疗方式：%s' % select_df.loc[id, '倾向治疗方式'])
                c2.markdown('')

                rec_df, med_type = phy_recommend(select_df.loc[id, '倾向治疗区域'], select_df.loc[id, '倾向治疗方式'])
                c3.markdown('<p class="label-font">诊疗推荐</p>', unsafe_allow_html=True)
                c3.write('推荐治疗方式：%s' % med_type)
                c3.markdown('<p class="label-font">推荐医疗机构/医生清单</p>', unsafe_allow_html=True)
                c3.table(rec_df)

                c2.markdown('<p class="label-font">进度管理</p>', unsafe_allow_html=True)
                cc = st.columns([0.87, 0.07, 0.8, 0.8, 0.8, 0.8, 0.07])
                theme_bad = {'bgcolor': '#f9f9f9', 'title_color': 'grey', 'content_color': 'grey',
                             'icon_color': 'grey', 'icon': 'fa fa-times-circle'}
                theme_ongoing = {'bgcolor': '#fcf8e5', 'title_color': 'orange', 'content_color': 'orange',
                                 'icon_color': 'orange', 'progress_color': 'orange', 'icon': 'fa fa-play-circle'}

                def info_card(name):
                    try:
                        if select_df.loc[id, name] != '':
                            if name == '住院记录':
                                state = select_df.loc[id, '住院状态']
                                if state == '入院后手术前':
                                    hc.info_card(title=name, content='最后日期：%s; 目前状态：手术前' % select_df.loc[id, name],
                                                 sentiment='neutral',
                                                 bar_value=33, theme_override=theme_ongoing)
                                elif state == '手术后出院前':
                                    hc.info_card(title=name, content='最后日期：%s; 目前状态：手术后出院前' % select_df.loc[id, name],
                                                 sentiment='neutral',
                                                 bar_value=66, theme_override=theme_ongoing)
                                elif state == '出院当日/后⼀日':
                                    hc.info_card(title=name, content='最后日期：%s; 目前状态：出院后' % select_df.loc[id, name],
                                                 sentiment='good',
                                                 bar_value=100)
                            else:
                                hc.info_card(title=name, content='最后日期：%s' % select_df.loc[id, name], sentiment='good',
                                             bar_value=100)
                        else:
                            hc.info_card(title=name, content='未进行', sentiment='bad', bar_value=0,
                                         theme_override=theme_bad)
                    except KeyError:
                        hc.info_card(title=name, content='未进行', sentiment='bad', bar_value=0, theme_override=theme_bad)

                with cc[2]:
                    info_card('数据采集')
                with cc[3]:
                    info_card('诊疗意见')
                with cc[4]:
                    info_card('住院记录')
                with cc[5]:
                    info_card('随访教育')

                ce, c1, ce, c2, ce = st.columns([0.07, 0.8, 0.07, 3.2, 0.07])
                with c2.expander(label='院前信息采集'):
                    def write_result(df, name: str, cols: list):
                        slice_df = pd.DataFrame(df, columns=cols)
                        slice_df = slice_df.where(slice_df.notnull(), '')
                        if len(slice_df) == 0:
                            return True
                        else:
                            # slice_df = slice_df[cols]
                            st.markdown('<p class="label-font">%s</p>' % name, unsafe_allow_html=True)
                            show_table(slice_df)
                            return True

                    write_result(details['症状体征'], '症状体征',
                                 ['症状', '程度', '类型', '持续时间（周）', '平均发作时长（小时）', '发作频次（次/周）', '录入时间'])
                    write_result(details['体格检查'], '体格检查', ['检查类型', '日期', '检查结果', '录入时间'])
                    write_result(details['影像学检查'], '影像学检查', ['检查类型', '日期', '检查结果', '录入时间'])
                    write_result(details['既往病史'], '既往病史', ['既往诊断', '患病时长（年）', '治疗方式', '名称', '时间', '疗程', '效果', '医疗机构',
                                                           '用法用量', '录入时间'])

                with c2.expander(label='随访结果'):
                    followup = db_followup.get(id)
                    slice_df = pd.DataFrame(followup['满意度问卷'], columns=['问题', '满意度', '答案'])
                    slice_df = slice_df.where(slice_df.notnull(), '')
                    show_table(slice_df)

            except IndexError:
                c2.error('未找到患者')
            print(datetime.datetime.now() - t1)
