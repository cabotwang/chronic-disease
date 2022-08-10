import streamlit as st
import pandas as pd
from Widget.Hydralit import HydraHeadApp
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

        @st.cache()
        def get_info_data():
            db_info = deta.Base("person_info")
            info = pd.DataFrame(db_info.fetch().items)
            return info

        @st.cache(allow_output_mutation=True)
        def get_data():
            return {}

        @st.cache(allow_output_mutation=True)
        def get_data_episode():
            return {}

        @st.cache()
        def get_medhis_data(key):
            med_info = deta.Base("medhis_info")
            medhis = med_info.get(key)
            return medhis

        if "episode_button_clicked" not in st.session_state:
            st.session_state.episode_button_clicked = False
        deta = Deta(st.secrets["deta_key"])
        info = get_info_data()
        print(info)
        info_need = info[['姓名', '身份证号', '性别', '个案管理状态', '电话', '倾向治疗区域', '倾向治疗方式', '更新时间']]

        if not st.session_state.episode_button_clicked:
            c1, ce = st.columns([0.8, 3])
            c1.markdown('<p class="label-font">患者查询</p>', unsafe_allow_html=True)
            with c1.form("my_form"):
                name_id = st.text_input('输入姓名或者身份证号')
                search = st.form_submit_button('搜索')
                if search:
                    get_data().clear()
                    info = info[['姓名', '身份证号', '性别', '个案管理状态', '电话', '倾向治疗区域', '倾向治疗方式', '更新时间']]
                    if name_id.isdigit():
                        select_df = info[info['身份证号'].str.contains(name_id)]
                    else:
                        select_df = info[info['姓名'].str.contains(name_id)]
                    get_data().update(select_df.to_dict('list'))

            if name_id:
                df = pd.DataFrame.from_dict(get_data())
                if len(df) > 0:
                    selection = show_table(df)
                    modify = st.button('修改所选患者信息')
                    if modify:
                        get_data().update(selection["selected_rows"][0])
                        st.session_state.episode_button_clicked = True
                        st.experimental_rerun()
                else:
                    st.warning('未找到患者')
                    add = st.button('增加新患者信息')
            else:
                df = pd.DataFrame.from_dict(info_need)
                selection = show_table(df)
                modify = st.button('查看患者信息')
                if modify:
                    get_data().update(selection["selected_rows"][0])
                    st.session_state.episode_button_clicked = True
                    st.experimental_rerun()
        else:
            st.markdown('<p class="label-font2">患者查询 > 病情信息</p>', unsafe_allow_html=True)
            c1, c2 = st.columns([1, 2])
            c1.markdown('<p class="label-font">个人基础信息</p>', unsafe_allow_html=True)
            c1.markdown('<p class="label-font2">患者姓名：%s </p>' % get_data()['姓名'], unsafe_allow_html=True)
            c1.markdown('<p class="label-font2">患者姓别：%s </p>' % get_data()['性别'], unsafe_allow_html=True)
            c1.markdown('<p class="label-font2">联系方式：%s </p>' % get_data()['电话'], unsafe_allow_html=True)
            c1.markdown('<p class="label-font2">身份证号：%s </p>' % get_data()['身份证号'], unsafe_allow_html=True)
            c1.markdown('<p class="label-font2">状态：%s </p>' % get_data()['个案管理状态'], unsafe_allow_html=True)
            c1.markdown('<p class="label-font2">更新时间：%s </p>' % get_data()['更新时间'], unsafe_allow_html=True)

            rec_df, med_type = phy_recommend(get_data()['倾向治疗区域'], get_data()['倾向治疗方式'])
            c2.markdown('<p class="label-font">诊疗推荐</p>', unsafe_allow_html=True)
            c2.write('推荐治疗方式：%s' % med_type)
            c2.markdown('<p class="label-font">推荐医疗机构/医生清单</p>', unsafe_allow_html=True)
            c2.table(rec_df)

            # st.markdown('<p class="label-font">进度管理</p>', unsafe_allow_html=True)
            # cc = st.columns([0.87, 0.07, 0.8, 0.8, 0.8, 0.8, 0.07])
            # theme_bad = {'bgcolor': '#f9f9f9', 'title_color': 'grey', 'content_color': 'grey',
            #              'icon_color': 'grey', 'icon': 'fa fa-times-circle'}
            # theme_ongoing = {'bgcolor': '#fcf8e5', 'title_color': 'orange', 'content_color': 'orange',
            #                  'icon_color': 'orange', 'progress_color': 'orange', 'icon': 'fa fa-play-circle'}
            #
            # def info_card(name):
            #     try:
            #         if info.loc[id, name] != '':
            #             if name == '住院记录':
            #                 state = select_df.loc[id, '住院状态']
            #                 if state == '入院后手术前':
            #                     hc.info_card(title=name, content='最后日期：%s; 目前状态：手术前' % select_df.loc[id, name],
            #                                  sentiment='neutral',
            #                                  bar_value=33, theme_override=theme_ongoing)
            #                 elif state == '手术后出院前':
            #                     hc.info_card(title=name, content='最后日期：%s; 目前状态：手术后出院前' % select_df.loc[id, name],
            #                                  sentiment='neutral',
            #                                  bar_value=66, theme_override=theme_ongoing)
            #                 elif state == '出院当日/后⼀日':
            #                     hc.info_card(title=name, content='最后日期：%s; 目前状态：出院后' % select_df.loc[id, name],
            #                                  sentiment='good',
            #                                  bar_value=100)
            #             else:
            #                 hc.info_card(title=name, content='最后日期：%s' % select_df.loc[id, name], sentiment='good',
            #                              bar_value=100)
            #         else:
            #             hc.info_card(title=name, content='未进行', sentiment='bad', bar_value=0,
            #                          theme_override=theme_bad)
            #     except KeyError:
            #         hc.info_card(title=name, content='未进行', sentiment='bad', bar_value=0, theme_override=theme_bad)
            #
            # with cc[2]:
            #     info_card('数据采集')
            # with cc[3]:
            #     info_card('诊疗意见')
            # with cc[4]:
            #     info_card('住院记录')
            # with cc[5]:
            #     info_card('随访教育')
            #
            # ce, c1, ce, c2, ce = st.columns([0.07, 0.8, 0.07, 3.2, 0.07])
            # with c2.expander(label='院前信息采集'):
            #     def write_result(df, name: str, cols: list):
            #         slice_df = pd.DataFrame(df, columns=cols)
            #         slice_df = slice_df.where(slice_df.notnull(), '')
            #         if len(slice_df) == 0:
            #             return True
            #         else:
            #             # slice_df = slice_df[cols]
            #             st.markdown('<p class="label-font">%s</p>' % name, unsafe_allow_html=True)
            #             show_table(slice_df)
            #             return True
            #
            #     write_result(details['症状体征'], '症状体征',
            #                  ['症状', '程度', '类型', '持续时间（周）', '平均发作时长（小时）', '发作频次（次/周）', '录入时间'])
            #     write_result(details['体格检查'], '体格检查', ['检查类型', '日期', '检查结果', '录入时间'])
            #     write_result(details['影像学检查'], '影像学检查', ['检查类型', '日期', '检查结果', '录入时间'])
            #     write_result(details['既往病史'], '既往病史', ['既往诊断', '患病时长（年）', '治疗方式', '名称', '时间', '疗程', '效果', '医疗机构',
            #                                            '用法用量', '录入时间'])

                # with c2.expander(label='随访结果'):
                #     followup = db_followup.get(id)
                #     slice_df = pd.DataFrame(followup['满意度问卷'], columns=['问题', '满意度', '答案'])
                #     slice_df = slice_df.where(slice_df.notnull(), '')
                #     show_table(slice_df)

            back = c2.button('退出本次管理')
            if back:
                st.session_state.episode_button_clicked = False
                st.experimental_rerun()
