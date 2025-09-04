import time

import pandas as pd
import streamlit as st
import numpy as np


st.sidebar.selectbox(
    'How would you like to be contacted?',
    ('Email', 'Home phone', 'Mobile phone')
)
st.sidebar.button("Run again")


with st.expander("expander"):
    st.title("Here is a title")
    st.write("Hello World")

    """
    My first app for test streamlit!\n
    The Magic!
    """
    "Magic command"

    df = pd.DataFrame({"A":[1,2,3],"B":[4,5,6]})
    df

    dataframe = pd.DataFrame(
        np.random.randn(10, 20),
        columns=('col %d' % i for i in range(20)))

    st.dataframe(dataframe.style.highlight_max(axis=0))

    chart_data =pd.DataFrame(
        np.random.randn(20,3),
        columns=['a','b','c'])

    st.line_chart(chart_data)

    map_data = pd.DataFrame(
        np.random.randn(1000, 2) / [50, 50] + [37.7, -122.4],
        columns=['lat', 'lon'])

    st.map(map_data)

    x = st.slider('x')
    st.write(x,'squared is',x * x,'asdf')

    st.text_input("Your name",key="name")

    st.success(st.session_state.name)
    st.warning('warning')
    st.info('info')
    st.error('error')

    st.checkbox('check')
    st.selectbox('box',(1,2,3))

    st.bar_chart({"data": [1,3,5,6,7,8,6]})
    st.image("https://static.streamlit.io/examples/dice.jpg")

    with st.echo():
        st.write('This code will be printed')

with st.expander("expander2"):
    left_column, right_column = st.columns(2)
    left_column.button('Press me!')

    # Or even better, call Streamlit functions inside a "with" block:
    with right_column:
        chosen = st.radio(
            'Sorting hat',
            ("Gryffindor", "Ravenclaw", "Hufflepuff", "Slytherin"))
        st.write(f"You are in {chosen} house!")

        with st.echo():
            if True:
                pass
                # print("Rerun")

    with st.echo():
        st.write('This code will be printed')

    #
    # with st.spinner("Wait for it...", show_time=True):
    #     time.sleep(5)
    #
    # latest_iteration = st.empty()
    # bar = st.progress(0)
    #
    # for i in range(100):
    #   # Update the progress bar with each iteration.
    #   latest_iteration.text(f'Iteration {i+1}')
    #   bar.progress(i + 1)
    #   time.sleep(0.1)

    '...and now we\'re done!'
with st.expander("Caching"):
    @st.cache_data
    def long_running_function(param1: int, param2: int):
        print("caching")
        st.write(f"CachingTest:{param1+param2}")
        return 0
    # 当参数更新或者更新了函数体时才会运行函数，否则不运行函数，输出缓存内容
    long_running_function(2,2)

    # 当counter不在session中时，创建并且初始化counter
    if "counter" not in st.session_state:
        st.session_state.counter = 0
        st.session_state.state1 = 0

    st.session_state.counter += 1
    st.header(f"This page has run  {st.session_state.counter}")

    st.selectbox("select",(1,2,3),key="select1")
    st.write(st.session_state)

    # 重新运行（Rerun）不会修改数据，重新加载页面会修改数据
    if "df" not in st.session_state:
        st.session_state.df = pd.DataFrame(np.random.randn(20, 2), columns=["x", "y"])

    color = st.color_picker("Color", "#FF0000")
    st.divider()
    st.scatter_chart(st.session_state.df, x="x", y="y", color=color)

    # 重新加载网页也不会修改数据
    @st.cache_data
    def cache_test(param1,param2):
        df = pd.DataFrame(np.random.randn(param1, param2), columns=["x", "y"])
        return df
    # st.write(cache_test(30,2))
    st.scatter_chart(cache_test(30,2),x="x", y="y", color=color)

with st.expander("数据库连接"):
    st.header("MysqlDatabase Connect")
    conn = st.connection("fish")
    df = conn.query("select * from dish")
    st.dataframe(df)


with st.expander("二次选择错误"):
    if "batch_generation_mode" not in st.session_state:
        st.session_state.batch_generation_mode = False
    """
        重新加载网页：
        session:False (batch_generation_mode)
        index:0 (radio)
        
        点击 M 选项（页面重新运行）：
        session:True
        index:1
        
        点击 S 选项（二次选择问题出现）：
        session:True
        index:1
        原因：动态生成index导致，使用静态的值就不会出问题
        使用了动态index会在下次**重新加载**时显示上次选择的值，类似于cache
        
        根本原因：
        状态更新的时序问题：
        st.radio 的 index 参数在组件渲染时就被确定
        而 st.session_state 的更新发生在用户交互之后
        这造成了一个状态滞后的问题：界面显示的是"上一次"的状态，而不是当前选择的状态
    """
    generation_mode = st.radio(
        "Batch Generation Mode",
        options=["Single Video Mode", "Multi Video Mode"],
        index=0 if not st.session_state["batch_generation_mode"] else 1,
        # index=1,
        horizontal=True
    )
    st.write(generation_mode)
    selected_index = ["Single Video Mode", "Multi Video Mode"].index(generation_mode)
    st.write(f"Selected index: {selected_index}")
    st.session_state["batch_generation_mode"] = (generation_mode == "Multi Video Mode")
    st.write(st.session_state)
