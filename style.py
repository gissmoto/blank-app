import streamlit as st

def apply_css():
    st.markdown(
        """
        <style>
        .icon {
            display: inline-block;
            margin-right: 5px;
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }
        .red { background-color: #FF0000; }
        .green { background-color: #00FF00; }
        .orange { background-color: #FFA500; }
        </style>
        """,
        unsafe_allow_html=True
    )
