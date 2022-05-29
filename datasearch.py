import streamlit as st
import pandas as pd
from hydralit import HydraHeadApp
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from deta import Deta
import datetime


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

        ce, c1, ce, c2, ce = st.columns([0.07, 1, 0.07, 3, 0.07])
        person_name = c1.text_input('按姓名搜索')
        person_id = c1.text_input('按身份证号搜索')
        search = c1.button('搜索')
        if search:
            t1 = datetime.datetime.now()
            deta = Deta(st.secrets["deta_key"])
            db_info = deta.Base("person_info")
            db_details = deta.Base("details_info")
            # db_symptom = deta.Base("person_symptom")
            # db_image = deta.Base("imaging")
            # db_physical = deta.Base("physical_test")
            # db_PMH = deta.Base('PMH')
            person_df = pd.DataFrame(db_info.fetch().items)
            details_df = pd.DataFrame(db_details.fetch().items)
            details_df = details_df.where(details_df.notnull(), '')

            with c2:
                if person_id != '':
                    select_df = person_df[person_df['身份证号'] == person_id]
                else:
                    select_df = person_df[person_df['姓名'] == person_name]
                # try:
                    id = select_df['身份证号'].tolist()[0]
                    select_df = select_df.set_index('身份证号')
                    st.markdown('<p class="label-font">个人基础信息</p>', unsafe_allow_html=True)
                    st.write('患者姓名：%s' % select_df.loc[id, '姓名'])
                    st.write('患者姓别：%s' % select_df.loc[id, '性别'])
                    st.write('联系方式：%s' % select_df.loc[id, '电话'])
                    st.write('身份证：%s' % id)
                    st.markdown('')
                    details_df = details_df[details_df['身份证号'] == id]

                    def write_result(df: pd.DataFrame, name: str, cols: list):
                        slice_df = df[df['数据类型'] == name]
                        print(slice_df)
                        if len(slice_df) == 0:
                            return True
                        else:
                            # slice_df.drop(columns=['key', '身份证号', '类型'], inplace=True)
                            slice_df = slice_df[cols]
                            st.markdown('<p class="label-font">%s</p>' % name, unsafe_allow_html=True)
                            show_table(slice_df)
                            return True

                    write_result(details_df, '症状体征', ['症状', '程度', '类型', '持续时间（周）', '平均发作时长（小时）', '发作频次（次/周）', '录入时间'])
                    write_result(details_df, '体格检查', ['检查类型', '日期', '检查结果', '录入时间'])
                    write_result(details_df, '影像学检查', ['检查类型', '日期', '检查结果', '录入时间'])
                    write_result(details_df, '既往病史', ['既往诊断', '患病时长（年）', '治疗方式', '名称', '时间', '疗程', '效果', '医疗机构',
                                                  '用法用量', '录入时间'])

                # except:
                #     st.error('未找到患者')
                print(datetime.datetime.now() - t1)