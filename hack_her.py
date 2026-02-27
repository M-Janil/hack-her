import streamlit as st
import pandas as pd
import difflib
from geopy.distance import geodesic
import webbrowser

# --- CONFIGURATION ---
st.set_page_config(page_title="LowKey Deals", layout="wide")

# --- 1. THEME (Kept exactly as you requested) ---
def apply_theme():
    st.markdown("""
        <style>
        html, body, [data-testid="stHeader"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, label, span, .stRadio p {
            color: #000000 !important;
            font-weight: 500;
        }
        .stTextInput label { color: #000000 !important; font-weight: bold !important; }
        .stApp { background-color: #FFFFFF; }
        input { color: #000000 !important; background-color: #F0F2F6 !important; border: 2px solid #8B4513 !important; }
        div.stButton > button { background-color: #8B4513 !important; color: #FFFFFF !important; font-weight: bold; border: none; }
        [data-testid="stSidebar"] { background-color: #F5F5DC !important; }
        .store-card { border: 1px solid #8B4513; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
        </style>
    """, unsafe_allow_html=True)

# --- 2. DATA INITIALIZATION (Fixes the AttributeError) ---
def init_data():
    # User's current location (Kerala, India)
    if 'user_location' not in st.session_state:
        st.session_state.user_location = (10.8505, 76.2711)

    if 'items' not in st.session_state:
        # Mocking items with linked store data
        st.session_state.items = {
            "Samsung Refrigerator": {
                "desc": "Double door, 250L Digital Inverter",
                "stores": [
                    {"name": "Electronic Plaza", "price": 24500, "coords": (10.8520, 76.2750), "rating": 4.5},
                    {"name": "Home Comforts", "price": 26000, "coords": (10.8400, 76.2600), "rating": 4.2}
                ]
            },
            "Washing Machine": {
                "desc": "Front load, 7kg Fully Automatic",
                "stores": [
                    {"name": "City Retail", "price": 17500, "coords": (10.8600, 76.2800), "rating": 4.0},
                    {"name": "Digital Hub", "price": 18200, "coords": (10.8300, 76.2500), "rating": 4.8}
                ]
            }
        }
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

# --- 3. UI FUNCTIONS ---
def get_google_maps_url(coords):
    return f"https://www.google.com/maps?q={coords[0]},{coords[1]}"

def home_page():
    st.title("LowKey Deals")
    st.markdown("### *Lowkey the best prices near you.*")
    
    # --- SEARCH BAR ---
    search_input = st.text_input("🔍 Search for appliances (e.g., 'Samsung' or 'Washing Machine')...", key="main_search")
    
    if search_input:
        all_item_names = list(st.session_state.items.keys())
        matches = difflib.get_close_matches(search_input, all_item_names, n=3, cutoff=0.2)
        
        if matches:
            st.markdown(f"#### Results for '{matches[0]}'")
            item_data = st.session_state.items[matches[0]]
            st.write(item_data['desc'])
            
            st.divider()
            st.subheader("Available Stores Near You")
            
            # Show store list with distance
            for store in item_data['stores']:
                dist = round(geodesic(st.session_state.user_location, store['coords']).km, 2)
                
                with st.container():
                    st.markdown(f"""
                    <div class="store-card">
                        <h4 style="margin:0;">🏪 {store['name']}</h4>
                        <p style="color:#8B4513; font-size:1.2rem; font-weight:bold; margin:5px 0;">Price: ₹{store['price']}</p>
                        <p style="margin:0;">📍 Distance: {dist} km away</p>
                        <p style="margin:0;">⭐ Rating: {store['rating']}/5</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Open in Google Maps ({store['name']})", key=store['name']):
                        url = get_google_maps_url(store['coords'])
                        st.write(f"Click here: [Google Maps Link]({url})")
        else:
            st.warning("No matches found. Try 'Samsung' or 'Washing Machine'.")
    
    st.divider()
    st.header("All Items")
    cols = st.columns(2)
    for i, (name, info) in enumerate(st.session_state.items.items()):
        with cols[i % 2]:
            st.subheader(name)
            st.write(info['desc'])
            if st.button(f"View Store Prices", key=f"btn_{name}"):
                st.info("Use the search bar above to see specific store distances for this item!")

# --- 4. EXECUTION ---
apply_theme()
init_data()

if not st.session_state.authenticated:
    # Simplified login to get you past the first screen
    st.title("Welcome to LowKey Deals")
    user = st.text_input("Username")
    if st.button("Login"):
        st.session_state.authenticated = True
        st.rerun()
else:
    with st.sidebar:
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()
    home_page()
