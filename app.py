import pandas as pd
from phone import Phone
import streamlit as st
from pyecharts import options as opts
from pyecharts.charts import Map

# 上传Excel文件
st.title("手机号归属地查询地图")
uploaded_file = st.file_uploader("上传Excel文件", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, sheet_name='Sheet1')

    # 初始化Phone对象
    p = Phone()
    # 创建一个新的DataFrame来存储归属地信息
    df_location = pd.DataFrame(columns=['call_number', 'province', 'city'])

    # 查询每个手机号的归属地并存储结果
    for index, row in df.iterrows():
        tel = row['call_number']
        location_info = p.find(tel)
        if location_info:  # 确保find方法返回了结果
            df_location = df_location._append({
                'call_number': tel,
                'province': location_info['province'],
                'city': location_info['city']
            }, ignore_index=True)

    # 按province统计数量
    province_counts = df_location.groupby('province').size()
    # 将结果存储为DataFrame（如果需要索引作为列）
    province_counts_df = province_counts.reset_index(name='count')


    # 或者，如果你只需要Series（即索引就是province）
    # province_counts = df_location.groupby('province').size()

    # 定义一个函数来修改province的值
    def modify_province(province):
        if province in ['北京', '天津', '上海', '重庆']:
            return province + '市'
        elif province in ['内蒙古', '西藏']:
            return province + '自治区'
        elif province == '广西':
            return province + '壮族自治区'
        elif province == '宁夏':
            return province + '回族自治区'
        elif province == '新疆':
            return province + '维吾尔自治区'
        else:
            return province + '省'


    # 使用apply函数和lambda表达式来应用修改函数
    province_counts_df['province'] = province_counts_df['province'].apply(lambda x: modify_province(x))

    # 显示修改后的DataFrame
    print(province_counts_df)

    # 2. 当province为浙江时，按city统计数量
    zhejiang_city_counts = df_location[df_location['province'] == '浙江'].groupby('city').size()
    zhejiang_city_counts_df = zhejiang_city_counts.reset_index(name='count')
    zhejiang_city_counts_df['city'] = zhejiang_city_counts_df['city'] + '市'
    # print(zhejiang_city_counts_df)

    c1 = (
        Map()
        .add('', [list(z) for z in zip(zhejiang_city_counts_df['city'].values.tolist(),
                                       zhejiang_city_counts_df['count'].values.tolist())], "浙江",
             label_opts=opts.LabelOpts(is_show=True, formatter="{b}: {c}")
             )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="浙江省呼入归属地分析"),
            visualmap_opts=opts.VisualMapOpts()
        )
        # .render("map_guangdong.html")
    )
    st.components.v1.html(c1.render_embed(), height=600)

    c2 = (
        Map()
        .add('', [list(z) for z in
                  zip(province_counts_df['province'].values.tolist(), province_counts_df['count'].values.tolist())],
             "china",
             label_opts=opts.LabelOpts(is_show=True, formatter="{b}: {c}")
             )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="全国呼入归属地分析"),
            visualmap_opts=opts.VisualMapOpts()  # 分段 is_piecewise=True
        )
        # .render("map_guangdong.html")
    )
    st.components.v1.html(c2.render_embed(), height=600)


