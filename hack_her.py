import streamlit as st
import pandas as pd
from datetime import datetime
import difflib
from geopy.distance import geodesic

# --- CONFIGURATION & THEME ---
st.set_page_config(page_title="LowKey Deals", page_icon="🏷️", layout="wide")

def apply_custom_theme():
    st.markdown("""
        <style>
        /* 1. Global text color for visibility on white background */
        html, body, [data-testid="stHeader"], .stMarkdown, p, h1, h2, h3, h4, h5, h6 {
            color: #000000 !important;
        }

        /* 2. Fix Labels (Username, Password, Select Role) to be Black */
        label, .stRadio p {
            color: #000000 !important;
            font-weight: bold !important;
        }

        /* 3. Main App Background */
        .stApp {
            background-color: #FFFFFF;
        }

        /* 4. Input Boxes - Keep text white or light gray for contrast against dark input fields */
        input {
            color: #FFFFFF !important;
        }
        
        /* 5. Buttons - Brown background with white text */
        div.stButton > button {
            background-color: #8B4513;
            color: #FFFFFF !important;
            border-radius: 5px;
            border: 1px solid #000000;
        }
        
        /* 6. Sale Badge */
        .sale-badge {
            background-color: #8B4513;
            color: #FFFFFF !important;
            padding: 4px 10px;
            border-radius: 10px;
            font-size: 0.9rem;
            font-weight: bold;
        }

        /* 7. Sidebar text */
        [data-testid="stSidebar"] section {
            color: #000000 !important;
        }
        </style>
    """, unsafe_allow_html=True)

# --- MOCK DATA INITIALIZATION ---
def init_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.role = None
        st.session_state.username = None

    st.session_state.user_coords = (9.9312, 76.2673)

    if 'items' not in st.session_state:
        st.session_state.items = {
            "Refrigerator": {"desc": "Double door, 250L", "category": "Kitchen"},
            "Washing Machine": {"desc": "Front load, 7kg", "category": "Laundry"},
            "Microwave Oven": {"desc": "Convection, 20L", "category": "Kitchen"},
            "Air Conditioner": {"desc": "1.5 Ton, 5 Star", "category": "Living"},
        }

    if 'stores' not in st.session_state:
        st.session_state.stores = [
            {"id": 1, "name": "Brown's Appliances", "lat": 9.9400, "lon": 76.2600, "open": "09:00", "close": "21:00", "rating": 4.5, "seller": "seller1"},
            {"id": 2, "name": "City Electronics", "lat": 9.9200, "lon": 76.2800, "open": "10:00", "close": "22:00", "rating": 3.8, "seller": "admin"},
        ]

    if 'inventory' not in st.session_state:
        st.session_state.inventory = [
            {"store_id": 1, "item": "Refrigerator", "price": 25000, "on_sale": True},
            {"store_id": 2, "item": "Refrigerator", "price": 27000, "on_sale": False},
        ]

    if 'reviews' not in st.session_state:
        st.session_state.reviews = []

# --- UTILITY ---
def get_distance(coords1, coords2):
    return round(geodesic(coords1, coords2).km, 2)

# --- PAGES ---
def login_page():
    st.title("Welcome to LowKey Deals")
    role = st.radio("Select Role", ["User", "Seller"])
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if (role == "User" and username in ["user1", "admin"]) or \
           (role == "Seller" and username in ["seller1", "admin"]):
            st.session_state.authenticated = True
            st.session_state.role = role
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Invalid credentials.")

def home_page():
    st.title("LowKey Deals")
    st.write("Lowkey the best prices near you.")
    
    search_query = st.text_input("🔍 Search appliances...")
    if search_query:
        matches = difflib.get_close_matches(search_query, st.session_state.items.keys(), n=3, cutoff=0.3)
        for match in matches:
            if st.button(f"Go to {match}"):
                st.session_state.search_selection = match
                st.rerun()

    st.divider()
    st.subheader("Available Items")
    cols = st.columns(2)
    for i, (item, info) in enumerate(st.session_state.items.items()):
        with cols[i % 2]:
            st.write(f"### {item}")
            st.write(info['desc'])
            if st.button(f"View Deals", key=item):
                st.session_state.search_selection = item
                st.rerun()

# --- APP EXECUTION ---
apply_custom_theme()
init_session_state()

if not st.session_state.authenticated:
    login_page()
else:
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()
    
    if 'search_selection' in st.session_state:
        # Simple back button for demo
        if st.button("Back"):
            del st.session_state.search_selection
            st.rerun()
        st.write(f"Showing deals for: {st.session_state.search_selection}")
    else:
        home_page()
