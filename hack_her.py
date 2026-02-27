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

        /* Make the Input Labels specifically bold and black */
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

        /* Style the Buttons */
        div.stButton > button {
            background-color: #8B4513 !important;
            color: #FFFFFF !important;
            font-weight: bold;
            border: none;
            padding: 10px 30px;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #F5F5DC !important;
        }
        </style>
    """, unsafe_allow_html=True)

# --- 2. DATA INITIALIZATION ---
def init_data():
    if 'items' not in st.session_state:
        st.session_state.items = {
            "Refrigerator": {"desc": "Double door, 250L", "price": 25000},
            "Washing Machine": {"desc": "Front load, 7kg", "price": 18000},
            "Microwave Oven": {"desc": "Convection, 20L", "price": 8500},
            "Air Conditioner": {"desc": "1.5 Ton, 5 Star", "price": 35000},
            "Vacuum Cleaner": {"desc": "Handheld, Cordless", "price": 12000},
            "Dishwasher": {"desc": "12 Place Settings", "price": 45000}
        }
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""

# --- 3. UI PAGES ---
def login_page():
    st.title("Welcome to LowKey Deals")
    st.radio("Select Role", ["User", "Seller"], key="role_selection")
    
    user = st.text_input("Username", key="user_input")
    pw = st.text_input("Password", type="password", key="pw_input")
    
    if st.button("Login"):
        if user:
            st.session_state.authenticated = True
            st.session_state.username = user
            st.rerun()

def home_page():
    st.title("LowKey Deals")
    st.markdown("### *Lowkey the best prices near you.*")
    
    # --- SEARCH BAR SECTION ---
    st.markdown("---")
    search_input = st.text_input("🔍 Search for appliances...", placeholder="Type 'Fridge' or 'Oven'...", key="main_search")
    
    if search_input:
        # Fuzzy matching logic
        all_items = list(st.session_state.items.keys())
        suggestions = difflib.get_close_matches(search_input, all_items, n=3, cutoff=0.3)
        
        if suggestions:
            st.write("Did you mean:")
            cols = st.columns(len(suggestions))
            for i, suggestion in enumerate(suggestions):
                if cols[i].button(f"👉 {suggestion}", key=f"sug_{suggestion}"):
                    st.session_state.selected_item = suggestion
                    st.rerun()
    
    st.markdown("---")
    
    # Display Details for selected item or general list
    if 'selected_item' in st.session_state:
        item_name = st.session_state.selected_item
        st.subheader(f"Results for: {item_name}")
        st.write(st.session_state.items[item_name]['desc'])
        st.write(f"**Best Price: ₹{st.session_state.items[item_name]['price']}**")
        if st.button("Back to All Items"):
            del st.session_state.selected_item
            st.rerun()
    else:
        st.header("Featured Appliances")
        items = st.session_state.get('items', {})
        cols = st.columns(2)
        for i, (name, info) in enumerate(items.items()):
            with cols[i % 2]:
                st.markdown(f"#### {name}")
                st.write(info['desc'])
                st.write(f"**Price: ₹{info['price']}**")
                if st.button(f"View Details", key=f"home_btn_{name}"):
                    st.session_state.selected_item = name
                    st.rerun()

# --- 4. EXECUTION FLOW ---
apply_theme()
init_data()

if not st.session_state.authenticated:
    login_page()
else:
    with st.sidebar:
        st.markdown(f"### Logged in: {st.session_state.username}")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()
    home_page() 
