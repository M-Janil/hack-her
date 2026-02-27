import streamlit as st
import pandas as pd
import difflib

# --- CONFIGURATION ---
st.set_page_config(page_title="LowKey Deals", layout="wide", initial_sidebar_state="expanded")

# --- 1. ENHANCED THEME ---
def apply_theme():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

        /* Global Overrides */
        html, body, [data-testid="stHeader"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, label {
            font-family: 'Inter', sans-serif !important;
            color: #3E2723 !important; /* Deep Brown */
        }

        .stApp {
            background-color: #FFFFFF;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #FDF5E6 !important; /* Old Lace / Cream */
            border-right: 1px solid #E0C097;
        }

        /* Input Box Styling */
        div[data-baseweb="input"] {
            background-color: #F8F5F2 !important;
            border-radius: 10px !important;
            border: 1px solid #D7CCC8 !important;
        }

        /* Hero Section */
        .hero-container {
            background-color: #5D4037; /* Medium Brown */
            padding: 3rem;
            border-radius: 20px;
            color: white !important;
            text-align: center;
            margin-bottom: 2rem;
        }
        .hero-container h1 { color: white !important; }

        /* Card Styling */
        .appliance-card {
            background-color: #FFFFFF;
            padding: 20px;
            border-radius: 15px;
            border: 1px solid #EFEBE9;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: transform 0.2s;
            margin-bottom: 20px;
            height: 250px;
        }
        .appliance-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 15px rgba(62, 39, 35, 0.1);
        }

        /* Button Styling */
        .stButton > button {
            width: 100%;
            border-radius: 8px !important;
            background-color: #795548 !important; /* Terracotta Brown */
            color: white !important;
            border: none !important;
            padding: 0.5rem 1rem !important;
            transition: 0.3s !important;
        }
        .stButton > button:hover {
            background-color: #3E2723 !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
        }
        </style>
    """, unsafe_allow_html=True)

# --- 2. DATA INITIALIZATION ---
def init_data():
    if 'items' not in st.session_state:
        st.session_state.items = {
            "Refrigerator": {"desc": "Double door, 250L", "price": "25,000", "icon": "❄️"},
            "Washing Machine": {"desc": "Front load, 7kg", "price": "18,000", "icon": "🧺"},
            "Microwave Oven": {"desc": "Convection, 20L", "price": "8,500", "icon": "🍲"},
            "Air Conditioner": {"desc": "1.5 Ton, 5 Star", "price": "35,000", "icon": "💨"},
            "Vacuum Cleaner": {"desc": "Handheld, Cordless", "price": "12,000", "icon": "🧹"},
            "Dishwasher": {"desc": "12 Place Settings", "price": "45,000", "icon": "🍽️"}
        }
    if 'authenticated' not in st.session_state: st.session_state.authenticated = False

# --- 3. UI PAGES ---
def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='text-align: center; padding: 40px;'><h1>LowKey Deals</h1><p>Premium Savings, Simplified.</p></div>", unsafe_allow_html=True)
        with st.container():
            st.radio("Account Type", ["Buyer", "Seller"], horizontal=True)
            user = st.text_input("Username")
            pw = st.text_input("Password", type="password")
            if st.button("Sign In"):
                if user:
                    st.session_state.authenticated = True
                    st.session_state.username = user
                    st.rerun()

def home_page():
    # Hero Header
    st.markdown("""
        <div class="hero-container">
            <h1>Discover Premium Deals</h1>
            <p style="color: #D7CCC8 !important;">Curated home appliances at low-key prices.</p>
        </div>
    """, unsafe_allow_html=True)

    # Search Logic
    search_col1, search_col2 = st.columns([3, 1])
    with search_col1:
        search_query = st.text_input("", placeholder="What are you looking for today?", label_visibility="collapsed")
    
    if search_query:
        matches = difflib.get_close_matches(search_query, list(st.session_state.items.keys()), n=3, cutoff=0.3)
        if matches:
            st.markdown(f"**Suggested:** " + " | ".join([f"`{m}`" for m in matches]))

    st.markdown("<br>", unsafe_allow_html=True)

    # Main Grid
    items = st.session_state.items
    cols = st.columns(3) # 3-Column Grid
    
    for i, (name, info) in enumerate(items.items()):
        with cols[i % 3]:
            st.markdown(f"""
                <div class="appliance-card">
                    <h3>{info['icon']} {name}</h3>
                    <p style="color: #757575 !important;">{info['desc']}</p>
                    <h2 style="color: #5D4037 !important;">₹{info['price']}</h2>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"Claim Deal", key=f"btn_{name}"):
                st.toast(f"Adding {name} to your watchlist!")

# --- 4. EXECUTION ---
apply_theme()
init_data()

if not st.session_state.authenticated:
    login_page()
else:
    with st.sidebar:
        st.markdown(f"### Welcome, **{st.session_state.username}**")
        st.markdown("---")
        st.button("My Orders")
        st.button("Settings")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()
    home_page()
