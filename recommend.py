import pandas as pd


# phy_df = pd.read_excel('Resource/Physician_List.xlsx', usecols=['属地', '类型', '医院', '医师', '专⻓'])
# phy_df = phy_df.where(phy_df.notnull(), None)
# phy_df.to_csv('Resource/Physician_List.csv', index=False, encoding='utf-8_sig')


def phy_recommend(area, med_type):
    # '无倾向', '本市', '外市'
    # '无倾向', '保守', '微创手术', '开放手术'
    phy_df = pd.read_csv('Resource/Physician_List.csv', usecols=['属地', '类型', '医院', '医师', '专⻓'])
    if area == '无倾向':
        area = '本市'
    # 只作为测试
    if med_type == '无倾向':
        med_type = '保守'
    selected_df = phy_df[(phy_df['专⻓'] == med_type) & (phy_df['类型'] == area)]
    selected_df = selected_df[['属地', '医院', '医师']]
    selected_df = selected_df.where(selected_df.notnull(), '').reset_index(drop=True)
    selected_df.index = selected_df.index+1
    return selected_df, med_type


phy_recommend('本市', '微创手术')


