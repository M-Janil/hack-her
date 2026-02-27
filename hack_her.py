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
        /* 1. FORCE ALL TEXT TO BLACK */
        /* This targets every possible text element in Streamlit */
        html, body, [data-testid="stHeader"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, label, span, .stRadio p {
            color: #000000 !important;
        }

        /* 2. MAIN BACKGROUND */
        .stApp {
            background-color: #FFFFFF;
        }

        /* 3. INPUT BOXES - Light background with BLACK text for visibility */
        input {
            color: #000000 !important;
            background-color: #f0f2f6 !important;
            border: 1px solid #8B4513 !important;
        }
        
        /* 4. BUTTONS - Brown background with white text */
        div.stButton > button {
            background-color: #8B4513 !important;
            color: #FFFFFF !important;
            border-radius: 5px;
            border: none;
            padding: 0.5rem 2rem;
        }
        
        /* 5. SIDEBAR - Black text on light brown */
        [data-testid="stSidebar"] {
            background-color: #f4ece1 !important;
        }
        [data-testid="stSidebar"] * {
            color: #000000 !important;
        }

        /* 6. EXPANDERS & CARDS */
        .streamlit-expanderHeader {
            color: #000000 !important;
            background-color: #FFFFFF !important;
        }
        </style>
    """, unsafe_allow_html=True)

# --- MOCK DATA INITIALIZATION ---
def init_session_state():
    # Ensure all keys exist to prevent AttributeErrors
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_coords' not in st.session_state:
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
    st.markdown("<h1>Welcome to LowKey Deals</h1>", unsafe_allow_html=True)
    
    # Selection text is now forced to black by CSS
    role = st.radio("Select Role", ["User", "Seller"])
    
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    
    if st.button("Login"):
        # Simple mock login logic
        if username and password:
            st.session_state.authenticated = True
            st.session_state.role = role
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Please enter both username and password.")

def home_page():
    st.markdown("<h1>LowKey Deals</h1>", unsafe_allow_html=True)
    st.markdown("<p>Lowkey the best prices near you.</p>", unsafe_allow_html=True)
    
    search_query = st.text_input("🔍 Search appliances...", key="main_search")
    
    if search_query:
        matches = difflib.get_close_matches(search_query, st.session_state.items.keys(), n=3, cutoff=0.3)
        if matches:
            st.write("Suggestions:")
            for match in matches:
                if st.button(f"Go to {match}", key=f"search_{match}"):
                    st.session_state.search_selection = match
                    st.rerun()

    st.divider()
    st.markdown("### Available Items")
    
    # Safe check for items to prevent the AttributeError seen in your screenshot
    if "items" in st.session_state and st.session_state.items:
        items_dict = st.session_state.items
        cols = st.columns(2)
        for i, (item_name, info) in enumerate(items_dict.items()):
            with cols[i % 2]:
                st.markdown(f"#### {item_name}")
                st.write(info['desc'])
                if st.button(f"View Deals for {item_name}", key=f"btn_{item_name}"):
                    st.session_state.search_selection = item_name
                    st.rerun()
    else:
        st.warning("No items found in database.")

# --- APP EXECUTION ---
apply_custom_theme()
init_session_state()

# Logout logic in sidebar
if st.session_state.get('authenticated'):
    with st.sidebar:
        st.markdown(f"### Logged in as: {st.session_state.username}")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.role = None
            st.rerun()

# Page Routing
if not st.session_state.authenticated:
    login_page()
else:
    if 'search_selection' in st.session_state:
        if st.button("← Back to List"):
            del st.session_state.search_selection
            st.rerun()
        st.markdown(f"## Deals for {st.session_state.search_selection}")
        st.info("Proximity-based sorting and effort scores would appear here.")
    else:
        home_page()
