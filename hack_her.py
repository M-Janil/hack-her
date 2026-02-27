import streamlit as st
import pandas as pd
import difflib
from geopy.distance import geodesic

# --- CONFIGURATION ---
st.set_page_config(page_title="LowKey Deals", layout="wide")

# --- 1. CLEAN BROWN & WHITE THEME ---
def apply_theme():
    st.markdown("""
        <style>
        /* Background and Global Text */
        .stApp {
            background-color: #FFFFFF;
        }
        
        /* Force All Text to Black for visibility */
        h1, h2, h3, h4, p, label, span, .stRadio p {
            color: #000000 !important;
        }

        /* Input Boxes: White background with Brown border */
        .stTextInput>div>div>input {
            background-color: #FFFFFF !important;
            color: #000000 !important;
            border: 2px solid #8B4513 !important;
            border-radius: 4px !important;
        }

        /* Buttons: Solid Brown with White Text */
        div.stButton > button {
            background-color: #8B4513 !important;
            color: #FFFFFF !important;
            border-radius: 4px !important;
            border: none !important;
            width: 100%;
        }
        
        /* Store Card: Simple Brown Border, no overlap */
        .store-box {
            border: 2px solid #8B4513;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 8px;
            background-color: #FFFFFF;
        }

        /* Sidebar: Brown Background with White Text */
        [data-testid="stSidebar"] {
            background-color: #8B4513 !important;
        }
        [data-testid="stSidebar"] * {
            color: #FFFFFF !important;
        }
        
        /* Metric/Distance Styling */
        .dist-text {
            color: #8B4513;
            font-weight: bold;
            font-size: 1.1rem;
        }
        </style>
    """, unsafe_allow_html=True)

# --- 2. DATA INITIALIZATION ---
def init_data():
    if 'user_location' not in st.session_state:
        # Default Location: Kochi, Kerala
        st.session_state.user_location = (9.9312, 76.2673)

    if 'items' not in st.session_state:
        st.session_state.items = {
            "Samsung Refrigerator": {
                "desc": "Double door, 250L Digital Inverter",
                "stores": [
                    {"name": "Pittappillil Agencies", "price": 24500, "coords": (9.9700, 76.2800), "rating": 4.5},
                    {"name": "Nandilath G-Mart", "price": 25100, "coords": (9.9912, 76.3000), "rating": 4.1}
                ]
            },
            "Washing Machine": {
                "desc": "7kg Fully Automatic Front Load",
                "stores": [
                    {"name": "Reliance Digital", "price": 17800, "coords": (10.0100, 76.3200), "rating": 4.3},
                    {"name": "Bismi Connect", "price": 18500, "coords": (9.9200, 76.2500), "rating": 3.9}
                ]
            }
        }
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

# --- 3. MAIN UI ---
def home_page():
    st.markdown("<h1 style='color: #8B4513;'>LowKey Deals</h1>", unsafe_allow_html=True)
    st.write("The best prices near you, without the noise.")
    
    # Simple Search Bar
    search_query = st.text_input("🔍 Search for an appliance...", placeholder="e.g. Samsung")
    
    if search_query:
        # Fuzzy Matching
        choices = list(st.session_state.items.keys())
        matches = difflib.get_close_matches(search_query, choices, n=1, cutoff=0.2)
        
        if matches:
            item_name = matches[0]
            item_info = st.session_state.items[item_name]
            
            st.markdown(f"### Deals for {item_name}")
            st.caption(item_info['desc'])
            
            # Show Stores
            for store in item_info['stores']:
                # Calculate real-world distance
                dist = round(geodesic(st.session_state.user_location, store['coords']).km, 2)
                
                # Manual Card Construction (No overlap)
                st.markdown(f"""
                <div class="store-box">
                    <h4 style="margin:0; color:#8B4513;">{store['name']}</h4>
                    <p style="font-size: 1.3rem; font-weight: bold; margin: 10px 0;">₹{store['price']}</p>
                    <p class="dist-text">📍 {dist} km away</p>
                    <p style="margin:0;">⭐ Rating: {store['rating']}/5</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Google Maps Link
                map_link = f"https://www.google.com/maps?q={store['coords'][0]},{store['coords'][1]}"
                st.markdown(f"[View on Google Maps]({map_link})")
        else:
            st.error("No items found. Try searching 'Samsung' or 'Washing'.")

    st.divider()
    st.subheader("Browse All Appliances")
    
    items = st.session_state.items
    cols = st.columns(2)
    for i, (name, info) in enumerate(items.items()):
        with cols[i % 2]:
            st.markdown(f"**{name}**")
            if st.button(f"Find Stores for {name}", key=f"btn_{name}"):
                st.info(f"Type '{name}' in the search bar above to see specific store distances!")

# --- 4. EXECUTION ---
apply_theme()
init_data()

# Login Logic
if not st.session_state.authenticated:
    st.markdown("<h2 style='color: #8B4513;'>Login to LowKey</h2>", unsafe_allow_html=True)
    user = st.text_input("Username")
    if st.button("Login"):
        st.session_state.authenticated = True
        st.rerun()
else:
    with st.sidebar:
        st.write("### Welcome to LowKey")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()
    home_page()
