import streamlit as st
import pandas as pd
import difflib
from geopy.distance import geodesic

# --- CONFIGURATION ---
st.set_page_config(page_title="LowKey Deals", layout="wide")

# --- 1. THEME: FORCING BLACK TEXT & VISIBLE INPUTS ---
def apply_theme():
    st.markdown("""
        <style>
        /* Force EVERY label and piece of text to Black */
        html, body, [data-testid="stHeader"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, label, span, .stRadio p {
            color: #000000 !important;
            font-weight: 500;
        }

        /* Make the Input Labels (Username/Password) specifically bold and black */
        .stTextInput label, .stSelectbox label, .stRadio label {
            color: #000000 !important;
            font-size: 1.1rem !important;
            font-weight: bold !important;
        }

        /* Set Background to White */
        .stApp {
            background-color: #FFFFFF;
        }

        /* Style Input Boxes so they are visible with black text inside */
        input {
            color: #000000 !important;
            background-color: #F0F2F6 !important;
            border: 2px solid #8B4513 !important;
        }

        /* Style the Login Button */
        div.stButton > button {
            background-color: #8B4513 !important;
            color: #FFFFFF !important;
            font-weight: bold;
            border: none;
            padding: 10px 30px;
        }
        </style>
    """, unsafe_allow_html=True)

# --- 2. DATA INITIALIZATION (Prevents AttributeError) ---
def init_data():
    if 'items' not in st.session_state:
        st.session_state.items = {
            "Refrigerator": {"desc": "Double door, 250L", "price": 25000},
            "Washing Machine": {"desc": "Front load, 7kg", "price": 18000},
            "Microwave Oven": {"desc": "Convection, 20L", "price": 8500},
            "Air Conditioner": {"desc": "1.5 Ton, 5 Star", "price": 35000}
        }
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = ""

# --- 3. UI PAGES ---
def login_page():
    st.title("Welcome to LowKey Deals")
    st.radio("Select Role", ["User", "Seller"], key="role_selection")
    
    user = st.text_input("Username", key="user_input")
    pw = st.text_input("Password", type="password", key="pw_input")
    
    if st.button("Login"):
        if user: # Basic check for demo
            st.session_state.authenticated = True
            st.session_state.username = user
            st.rerun()

def home_page():
    st.title(f"LowKey Deals")
    st.write(f"Logged in as: {st.session_state.username}")
    
    st.divider()
    st.header("Available Items")
    
    # Using a safe get() to prevent the AttributeError seen in your screenshot
    items = st.session_state.get('items', {})
    
    cols = st.columns(2)
    for i, (name, info) in enumerate(items.items()):
        with cols[i % 2]:
            st.subheader(name)
            st.write(info['desc'])
            st.write(f"**Starting at: ₹{info['price']}**")
            st.button(f"View Deals for {name}", key=f"btn_{name}")

# --- 4. EXECUTION FLOW ---
# ALWAYS call these first!
apply_theme()
init_data()

if not st.session_state.authenticated:
    login_page()
else:
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()
    home_page()
