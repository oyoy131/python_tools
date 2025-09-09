import streamlit as st

st.title("page3")

with st.expander("莫名其妙没有错误了！"):

    concurrent_count = 3
    if "batch_scripts" not in st.session_state:
        st.session_state["batch_scripts"] = []

    st.session_state["batch_scripts"] = [""] * concurrent_count

    for i in range(concurrent_count):
        with st.expander(f"视频 {i + 1}", expanded=True):
            # 避免默认值多次初始化问题
            # 标题输入框，直接赋值法

            # 文案展示区域，回调函数法
            def update_shared_data(i: int, key_name: str):
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