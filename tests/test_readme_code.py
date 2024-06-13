import streamlit as st
import streamlit_execute as se

# Create an interpreter
response = se.init()

# Connect all run calls to the interpreter
se.connect()

# Execute code
response_add = se.run("5 + 5")
st.write(response_add)
