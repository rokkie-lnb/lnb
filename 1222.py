import streamlit as st
import re
import textwrap
import requests
import os
import jieba
from bs4 import BeautifulSoup
from collections import Counter
from pyecharts import options as opts
from pyecharts.charts import WordCloud, Bar, Pie, Line, Scatter, Funnel, Polar, Radar


def remove_html_tags(text):
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', text)


def remove_punctuation(text):
    punctuations = r'[\s+\.\!\/_,|$%^*(+\"\')+|[+——！，。？、~@#￥%……&*（）]+'
    return re.sub(punctuations, '', text)


def format_text(text, width=80):
    paragraphs = text.split('\n\n')
    formatted_text = []
    for p in paragraphs:
        lines = textwrap.wrap(p, width=width)
        formatted_text.append('\n'.join(lines))
    return '\n'.join(formatted_text)


def get_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    text = soup.get_text(strip=True)
    return remove_html_tags(text)


def plot_word_cloud(top_words):
    words, frequencies = zip(*top_words)
    c = WordCloud()
    c.add("", list(zip(words, frequencies)))
    c.set_global_opts(title_opts=opts.TitleOpts(title="Word Cloud"))
    return c


def plot_bar(top_words):
    words, frequencies = zip(*top_words)
    c = Bar()
    c.add_xaxis(list(words))
    c.add_yaxis("Frequency", list(frequencies))
    c.set_global_opts(title_opts=opts.TitleOpts(title="Word Frequency Bar Plot"))
    return c


def plot_pie(top_words):
    words, frequencies = zip(*top_words)
    pie = Pie(init_opts=opts.InitOpts(width="900px", height="500px"))

    # 对数据进行排序，更高的频率在前面
    top_words.sort(key=lambda x: x[1], reverse=True)

    # 添加数据，设置半径和弧度，设置透明度
    pie.add("", [(word[0], word[1]) for word in top_words],
            radius=["30%", "75%"],
            rosetype="area",
            itemstyle_opts=opts.ItemStyleOpts(opacity=0.8))

    # 全局设置项
    pie.set_global_opts(title_opts=opts.TitleOpts(title="Word Frequency Pie Chart: Top {} Words".format(len(top_words)),
                                                  pos_left="center"),
                        legend_opts=opts.LegendOpts(is_show=False),  # 不显示图例
                        toolbox_opts=opts.ToolboxOpts(orient='vertical'))  # 添加工具箱组件

    # 系列配置项，设置标签显示方式
    pie.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))

    return pie


def plot_line(top_words):
    words, frequencies = zip(*top_words)
    c = Line()
    c.add_xaxis(list(words))
    c.add_yaxis("Frequency", list(frequencies))
    c.set_global_opts(title_opts=opts.TitleOpts(title="Word Frequency Line Chart"))
    return c


def plot_scatter(top_words):
    words, frequencies = zip(*top_words)
    c = Scatter()
    c.add_xaxis(list(words))
    c.add_yaxis("Frequency", list(frequencies))
    c.set_global_opts(title_opts=opts.TitleOpts(title="Word Frequency Scatter Chart"))
    return c


def plot_funnel(top_words):
    words, frequencies = zip(*top_words)
    c = Funnel()
    c.add("", list(zip(words, frequencies)))
    c.set_global_opts(title_opts=opts.TitleOpts(title="Word Frequency Funnel Chart"))
    return c


def plot_polar(top_words):
    words, frequencies = zip(*top_words)
    c = Polar()
    c.add("", list(zip(words, frequencies)))
    c.set_global_opts(title_opts=opts.TitleOpts(title="Word Frequency Polar Chart"))
    return c


def plot_radar(top_words):
    words, frequencies = zip(*top_words)
    c = Radar()
    c.add_schema(schema=[opts.RadarIndicatorItem(name=w, max_=f) for w, f in top_words])
    c.add("", [frequencies])
    c.set_global_opts(title_opts=opts.TitleOpts(title="Word Frequency Radar Chart"))
    return c


def main():
    st.title('文本处理和词频统计')
    st.sidebar.title('选择操作')

    option = st.sidebar.radio('选择操作类型', ('上传文件', '输入URL'))
    chart_types = {
        "词云图": plot_word_cloud,
        "条形图": plot_bar,
        "饼状图": plot_pie,
        "线状图": plot_line,
        "散点图": plot_scatter,
        "漏斗图": plot_funnel,
        "极坐标图": plot_polar,
        "雷达图": plot_radar,
    }
    selected_chart_type = st.sidebar.selectbox("请选择图表类型", list(chart_types.keys()))
    num_words = st.sidebar.slider('选择需要显示的高频词的数量', 1, 100, 20)

    if option == '上传文件':
        file_path = st.file_uploader('请选择文件', type=["txt"])
        if file_path is not None:
            text = file_path.getvalue().decode("utf-8")
            formatted_text = format_text(text, width=80)
            st.text_area("原始文本预览", formatted_text, height=200)
            cleaned_text = remove_punctuation(text)
            jieba.setLogLevel(20)
            words = jieba.lcut(cleaned_text)
            word_counter = Counter(words)
            top_words = word_counter.most_common(num_words)
            selected_chart_func = chart_types[selected_chart_type]
            chart = selected_chart_func(top_words)
            st_pyecharts(chart)

            # 增加下载高频词
            if st.sidebar.button('下载高频词'):
                content = ''
                for word, frequency in top_words:
                    content += f'{word},{frequency}\n'
                st.sidebar.download_button(label='下载', data=content, file_name='高频词.csv', mime='text/csv')
        else:
            st.warning('请先上传文件')

    elif option == '输入URL':
        url = st.text_input('请输入URL')
        if url != '':
            text = get_text_from_url(url)
            cleaned_text = remove_punctuation(text)
            jieba.setLogLevel(20)
            words = jieba.lcut(cleaned_text)
            word_counter = Counter(words)
            top_words = word_counter.most_common(num_words)
            selected_chart_func = chart_types[selected_chart_type]
            chart = selected_chart_func(top_words)
            st_pyecharts(chart)




def st_pyecharts(chart):
    chart.render("temp_chart.html")
    with open("temp_chart.html", "r", encoding="utf-8") as f:
        html_code = f.read()
    st.components.v1.html(html_code, height=500)


if __name__ == "__main__":
    main()