import time

import pandas as pd
import streamlit as st
import numpy as np

st.set_page_config(
    page_title="Streamlit Test",
    page_icon="🍟",
    layout="wide"
)

st.sidebar.selectbox(
    'How would you like to be contacted?',
    ('Email', 'Home phone', 'Mobile phone')
)
st.sidebar.button("Run again")

plate =  st.columns(2)
left_plate = plate[0]
righ_palte = plate[1]

with left_plate:

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
        if "text_value" not in st.session_state:
            st.session_state.text_value = "默认值"
        """
            run1:
                重新加载页面（组件首次运行）
                内容都为默认值
                默认值 = 默认值内容
                
            run2：
                与组件交互，添加新内容
                Rerun
                因为默认值没有改变，所以组件的值修改成功（组件非首次运行）
                默认值 = 新的修改内容1
                
            run3：
                与组件交互，添加新内容
                Rerun
                默认值发生了改变，组件值修改失败，组件值变成默认值（也就是上一次运行新的修改内容1）（组件首次运行）
                默认值 = 新的修改内容1
                （这一次添加的新内容其实给吞了）
                
            run4：
                与组件交互，添加新内容
                Rerun
                默认值没有改变（还是新的修改内容1），组件值修改成功（组件非首次运行）
                默认值 = 新的修改内容2
                
            run5：
                与组件交互，添加新内容
                Rerun
                默认值发生了改变，组件修改失败，组件值变成默认值（也就是上一次运行新的修改内容2）（组件首次运行）
                默认值 = 新的修改内容2
                
            以此类推……
            
            解决方法：
            1. 不用动态修改主件的属性（每一次Rerun，组件的属性不要改变）
            2. 使用st.rerun()二次运行页面
            3. 使用回调函数修改默认值
        """

        generation_mode = st.radio(
            "Batch Generation Mode",
            options=["Single Video Mode", "Multi Video Mode"],
            index=0 if not st.session_state["batch_generation_mode"] else 1,
            # index=1,
            horizontal=True
        )


        st.text_area(
            label="text",
            value=st.session_state.text_value,
            key="text_key"
        )
        st.session_state.text_value = st.session_state.text_key


        st.divider()

        st.write(generation_mode)
        selected_index = ["Single Video Mode", "Multi Video Mode"].index(generation_mode)
        st.write(f"Selected index: {selected_index}")
        st.session_state["batch_generation_mode"] = (generation_mode == "Multi Video Mode")
        st.write(st.session_state)

    with st.expander("Streamlit 知识点"):
        """
        ### 多页面问题
        1. 使用多 page 时，每个页面在交互后会单独 Rerun，当重新加载页面时，所有页面会一起重载
        2. 区别页面单独 Rerun 和全页面全部重载的另一种状态：当页面切换时，切换到的页面中的组件的值会恢复到一个默认值，但是 session 依旧保留（待求解？）
            - Rerun 时并不会恢复默认值，而是使用 session 的值
            - 重载时会恢复默认值，但是也会将 session 的值重置
        """

    with st.expander("BUG"):
        "#### 使用字典的方式调用session_key导致识别失败问题"
        code = """
        st.button("Rerun")
        if "Rerun_Setting" not in st.session_state:
        st.session_state.Rerun_Setting = 0
        def info_session(session_key):
            # 如果使用点进行值的调用会导致 st 识别失败，将形参名识别为session的key，而不是形参的值
            # st.session_state.session_key = st.session_state.session_key + 1
            st.session_state[session_key] += 1
            st.write(f"{session_key}:{st.session_state[session_key]}")
            st.write(st.session_state)
    
        info_session("Rerun_Setting")
        """
        st.code(code,"python")

    # ========== 使用回调函数的双向同步方案 ==========
    # 初始化共享数据
    if "callback_data" not in st.session_state:
        st.session_state.callback_data = "回调方案初始数据"
    # 定义回调函数
    def update_shared_data():
        """当用户更改文本时调用的回调函数"""
        st.session_state.callback_data = st.session_state.callback_text_area
        # st.session_state.data_from = "user"
    def backend_update():
        """后台更新数据"""
        st.session_state.callback_data = f"后台更新数据 (时间: {pd.Timestamp.now()})"
        # st.session_state.data_from = "backend"

    with st.expander("回调函数双向同步"):
        # 显示当前数据来源
        # if "data_from" not in st.session_state:
        #     st.session_state.data_from = "initial"
        #
        # st.caption(f"数据来源: {st.session_state.data_from}")

        # 使用回调函数的文本框
        st.text_area(
            "回调同步文本框",
            value=st.session_state.callback_data,
            height=150,
            key="callback_text_area",
            on_change=update_shared_data  # 用户更改时调用回调，修改组件默认值（value）
        )

        # 后台更新按钮
        if st.button("后台更新（回调方案）"):
            backend_update()
            st.rerun()

        st.divider()

        # 显示当前数据
        st.write("**回调方案当前数据:**")
        st.code(st.session_state.callback_data)

    # ... existing code ...

    with st.expander("MoneyPrinter二次显示错误"):


        if "concurrent_count" not in st.session_state:
            st.session_state["concurrent_count"] = 1
        if "batch_titles" not in st.session_state:
            st.session_state["batch_titles"] = []
        if "batch_scripts" not in st.session_state:
            st.session_state["batch_scripts"] = []

        # 批量视频生成模块
        with st.container(border=True):
            st.write("Batch Video Generation")
            # # 生成模式选择
            # generation_mode = st.radio(
            #     "Batch Generation Mode",
            #     options=["Single Video Mode", "Multi Video Mode"],
            #     # index=0 if not st.session_state["batch_generation_mode"] else 1,
            #     key="aaa",
            #     index=0,
            #     horizontal=True
            # )
            # st.session_state["batch_generation_mode"] = (generation_mode == "Multi Video Mode")

            # if st.session_state["batch_generation_mode"]:
            if True:
                # 选择并发生成数量
                # concurrent_count = st.selectbox(
                #     "Concurrent Generation Count",
                #     options=[1, 2, 3, 4, 5],
                #     # index=st.session_state["concurrent_count"] - 1
                #     index=0
                # )
                concurrent_count = 2
                st.session_state["concurrent_count"] = concurrent_count
                # 生成输入框按钮
                if st.button("Generate Input Fields", key="generate_input_fields"): # !!!!!!!注释掉就不会有错误了!!!!!!!!!
                # if True:
                    # st.session_state["batch_titles"] = [""] * concurrent_count
                    st.session_state["batch_scripts"] = [""] * concurrent_count
                    # st.session_state["batch_materials"] = [[] for _ in range(concurrent_count)]
                # 动态生成标题输入框和文案展示区域
                # if len(st.session_state["batch_titles"]) == concurrent_count:
                if True:
                    for i in range(concurrent_count):
                        with st.expander(f"视频 {i + 1}", expanded=True):
                            # 避免默认值多次初始化问题
                            # # 标题输入框，直接赋值法
                            # title_key = f"batch_title_{i}"
                            # st.session_state["batch_titles"][i] = st.text_input(
                            #     "Video Title",
                            #     # value=st.session_state["batch_titles"][i],
                            #     key=title_key
                            # )
                            # 文案展示区域，回调函数法
                            def update_shared_data(i:int, key_name:str):
                                """当用户更改文本时调用的回调函数"""
                                st.session_state["batch_scripts"][i] = st.session_state[f"batch_script_{i}"]
                            #     st.write(st.session_state["batch_scripts"][i])
                            #     st.write(st.session_state[f"batch_script_{i}"])
                            #
                            script_key = f"batch_script_{i}"
                            if script_key not in st.session_state:
                                st.session_state[script_key] = "" # session 的名字是变量的时候应该怎么调用？

                            if len(st.session_state["batch_scripts"]) > i:
                                st.session_state["batch_scripts"][i] = st.text_area(
                                    "Generated Script",
                                    value=st.session_state["batch_scripts"][i],
                                    height=150,
                                    key=script_key,
                                    disabled=False,
                                    on_change=update_shared_data(i, script_key)
                                )




with righ_palte:

    st.button("Rerun")
    if "Rerun_Test" not in st.session_state:
        st.session_state.Rerun_Test = 0
    def info_session(session_key):
        # 如果使用点进行值的调用会导致 st 识别失败，将形参名识别为session的key，而不是形参的值
        # st.session_state.session_key = st.session_state.session_key + 1
        st.session_state[session_key] += 1
        st.write(f"{session_key}:{st.session_state[session_key]}")
        st.write(st.session_state)

    info_session("Rerun_Test")



