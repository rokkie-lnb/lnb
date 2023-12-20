import streamlit as st
import re
import textwrap
import jieba
import requests
from collections import Counter
import matplotlib.pyplot as plt
import os
from bs4 import BeautifulSoup
def remove_punctuation(text):
    punctuations = r'[\s+\.\!\/_,|$%^*(+\"\')+|[+——！，。？、~@#￥%……&*（）]+'
    return re.sub(punctuations, '', text)

def remove_html_tags(text):
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', text)

def format_text(text, width=80):
    paragraphs = text.split('\n\n')
    formatted_text = []
    for p in paragraphs:
        lines = textwrap.wrap(p, width=width)
        formatted_text.append('\n'.join(lines))
        formatted_text.append('')  # 添加额外空行
    return '\n'.join(formatted_text)

def plot_word_frequency(word_counter, n):
    top_words = word_counter.most_common(n)
    labels = [word for word, _ in top_words]
    frequencies = [freq for _, freq in top_words]

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用中文字体
    plt.rcParams['axes.unicode_minus'] = False  # 用于正常显示负号

    fig, ax = plt.subplots()

    ax.pie(frequencies, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.set_title(f'Top {n} Words Frequency')

    # 显示高频词
    text_str = "\n".join([f"{word}: {freq}" for word, freq in top_words])
    plt.text(1.2, 0.5, text_str, transform=ax.transAxes, fontsize=12, verticalalignment='center')

    ax.axis('equal')
    st.pyplot(fig)
def process_upload_file(file_path, top_n):
    text = file_path.getvalue().decode("utf-8")
    formatted_text = format_text(text, width=80)  # 格式化文本
    st.text_area("原始文本预览", formatted_text, height=200)  # 显示文本预览
    # 去除标点符号
    cleaned_text = remove_punctuation(text)
    # 分词并统计词频
    jieba.setLogLevel(20)  # 设置jieba分词日志级别，防止警告输出
    words = jieba.lcut(cleaned_text)
    word_counter = Counter(words)
    # 只保留前top_n个高频词
    top_words = word_counter.most_common(top_n)
    word_counter = Counter(dict(top_words))
    # 绘制词频最高的20个词的饼状图
    plot_word_frequency(word_counter, top_n)
    # 保存高频词到文件夹
    save_folder = "./output"
    os.makedirs(save_folder, exist_ok=True)
    file_name = f"high_frequency_words_top{top_n}.txt"
    save_file_path = os.path.join(save_folder, file_name)
    save_high_frequency_words(save_file_path, word_counter)
    st.success(f"高频词已成功保存至文件夹 {save_file_path}！")

def save_high_frequency_words(file_path, word_counter):
    top_words = word_counter.most_common()
    with open(file_path, 'w', encoding='utf-8') as file:
        for word, freq in top_words:
            file.write(f"{word}: {freq}\n")
def process_url(url, top_n):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    body = soup.body.get_text()
    text = remove_html_tags(body)
    text = remove_punctuation(text)

    # 分词并统计词频
    jieba.setLogLevel(20)  # 设置jieba分词日志级别，防止警告输出
    words = jieba.lcut(text)

    # 根据词频统计词语数目
    word_counter = Counter(words)

    # 只保留前top_n个高频词
    top_words = word_counter.most_common(top_n)
    word_counter = Counter(dict(top_words))

    # 绘制词频最高的20个词的饼状图
    plot_word_frequency(word_counter, top_n)

    # 保存文本到文件夹
    save_folder = "./output"
    os.makedirs(save_folder, exist_ok=True)
    file_name = f"text_from_url_top{top_n}.txt"
    save_file_path = os.path.join(save_folder, file_name)
    with open(save_file_path, 'w', encoding='utf-8') as file:
        file.write(text)
    st.success(f"文本已成功保存至文件夹 {save_file_path}！")
def main():
    st.title('文本处理和词频统计')
    st.sidebar.title('选择操作')
    top_n = st.sidebar.slider('选择词频统计的单词数目', 1, 50, 20)
    option = st.sidebar.radio('',
                              ('上传文件', '输入URL'),
                              key='nav_radio',
                              help="选择操作的方式")

    if option == '上传文件':
        file_path = st.file_uploader('请选择文件', type=["txt"])
        if st.button('确定') and file_path is not None:
            process_upload_file(file_path, top_n)
    elif option == '输入URL':
        url = st.text_input('请输入URL')
        if st.button('确定') and url != '':
            process_url(url, top_n)


if __name__ == "__main__":
    main()