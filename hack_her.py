import streamlit as st

st.title("Hack Her App")

st.write("This is my first Streamlit app 🎉")

name = st.text_input("Enter your name")

if st.button("Submit"):
    st.success(f"Hello {name}!")
