import streamlit as st
import pandas as pd
import difflib
from geopy.distance import geodesic

# --- CONFIGURATION ---
st.set_page_config(page_title="LowKey Deals", layout="wide")

# --- 1. CHARMING CUSTOM THEME ---
def apply_theme():
    st.markdown("""
        <style>
        /* Global Font and Background */
        html, body, [data-testid="stHeader"] {
            background-color: #FFFFFF;
        }
        
        /* Charming Typography */
        h1, h2, h3 {
            color: #3D2B1F !important; /* Deep Espresso Brown */
            font-family: 'Trebuchet MS', sans-serif;
            font-weight: 800 !important;
        }
        
        p, label, span, .stRadio p {
            color: #000000 !important;
            font-weight: 500;
        }

        /* Modern Input Boxes */
        .stTextInput>div>div>input {
            background-color: #FDF5E6 !important; /* Old Lace White */
            color: #000000 !important;
            border: 2px solid #8B4513 !important;
            border-radius: 15px !important;
            padding: 10px !important;
        }

        /* Charmy Store Cards */
        .store-card {
            background: #FFFFFF;
            border-left: 10px solid #8B4513;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 5px 5px 15px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            transition: transform 0.2s;
        }
        .store-card:hover {
            transform: translateY(-5px);
            box-shadow: 5px 5px 20px rgba(139, 69, 19, 0.2);
        }

        /* Buttons with a glow */
        div.stButton > button {
            background-color: #3D2B1F !important;
            color: #FFFFFF !important;
            border-radius: 12px !important;
            border: none !important;
            padding: 12px 24px !important;
            font-weight: bold !important;
            box-shadow: 0px 4px 6px rgba(0,0,0,0.2);
        }
        div.stButton > button:hover {
            background-color: #8B4513 !important;
            color: #FFFFFF !important;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #3D2B1F !important;
            border-right: 1px solid #000000;
        }
        [data-testid="stSidebar"] * {
            color: #FFFFFF !important;
        }
        
        /* Sale Badge */
        .sale-badge {
            background-color: #FFD700;
            color: #000000 !important;
            padding: 3px 10px;
            border-radius: 8px;
            font-size: 0.8rem;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

# --- 2. DATA INITIALIZATION ---
def init_data():
    if 'user_location' not in st.session_state:
        st.session_state.user_location = (10.8505, 76.2711) # Kerala Default

    # This is the "Database" of items and stores
    if 'items' not in st.session_state:
        st.session_state.items = {
            "Samsung Refrigerator": {
                "desc": "Double door, 250L Digital Inverter",
                "stores": [
                    {"name": "Espresso Electronics", "price": 24500, "coords": (10.8520, 76.2750), "rating": 4.5},
                    {"name": "Kerala Home Hub", "price": 26000, "coords": (10.8400, 76.2600), "rating": 4.2}
                ]
            },
            "Washing Machine": {
                "desc": "7kg Fully Automatic Front Load",
                "stores": [
                    {"name": "Brown & Black Retail", "price": 17500, "coords": (10.8600, 76.2800), "rating": 4.0}
                ]
            }
        }
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'role' not in st.session_state:
        st.session_state.role = "User"

# --- 3. SELLER FEATURE: HOW TO ADD STORES/PRICES ---
def seller_page():
    st.title("Seller Dashboard")
    st.markdown("### Upload New Deals")
    
    with st.form("add_deal_form"):
        item_choice = st.selectbox("Select Appliance", list(st.session_state.items.keys()))
        store_name = st.text_input("Your Store Name")
        price = st.number_input("Price (₹)", min_value=100)
        lat = st.number_input("Store Latitude", value=10.85)
        lon = st.number_input("Store Longitude", value=76.27)
        rating = st.slider("Store Rating", 1.0, 5.0, 4.0)
        
        submitted = st.form_submit_button("Post Deal")
        if submitted:
            new_store = {
                "name": store_name,
                "price": price,
                "coords": (lat, lon),
                "rating": rating
            }
            st.session_state.items[item_choice]["stores"].append(new_store)
            st.success(f"Deal for {item_choice} posted successfully!")

# --- 4. HOME PAGE ---
def home_page():
    st.markdown("<h1 style='text-align: center;'>LOWKEY DEALS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-style: italic;'>Elegant savings, just around the corner.</p>", unsafe_allow_html=True)
    
    # Elegant Search Bar
    search_input = st.text_input("🔍 What are you looking for today?", placeholder="e.g. Samsung Refrigerator")
    
    if search_input:
        matches = difflib.get_close_matches(search_input, list(st.session_state.items.keys()), n=1, cutoff=0.2)
        
        if matches:
            item_name = matches[0]
            item_data = st.session_state.items[item_name]
            st.markdown(f"## Deals for {item_name}")
            
            # Show Stores
            for store in item_data['stores']:
                dist = round(geodesic(st.session_state.user_location, store['coords']).km, 2)
                
                st.markdown(f"""
                <div class="store-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h3 style="margin:0;">{store['name']}</h3>
                        <span class="sale-badge">BEST PRICE</span>
                    </div>
                    <p style="font-size: 1.5rem; color: #8B4513; margin: 10px 0;">₹{store['price']}</p>
                    <p><b>📍 Location:</b> {dist} km away</p>
                    <p><b>⭐ Customer Rating:</b> {store['rating']}/5</p>
                    <p style="font-size: 0.8rem; color: #666;">Coordinates: {store['coords']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Maps Trigger
                map_url = f"https://www.google.com/maps?q={store['coords'][0]},{store['coords'][1]}"
                st.markdown(f"[Navigate with Google Maps]({map_url})")
        else:
            st.warning("We couldn't find that item. Try searching for 'Samsung'!")

    st.divider()
    
    # Grid of items
    st.markdown("### Featured Appliances")
    cols = st.columns(3)
    for i, (name, info) in enumerate(st.session_state.items.items()):
        with cols[i % 3]:
            st.markdown(f"**{name}**")
            st.caption(info['desc'])
            if st.button("Check Proximity", key=f"check_{name}"):
                st.info(f"Search for '{name}' above to see the map!")

# --- 5. EXECUTION ---
apply_theme()
init_data()

if not st.session_state.authenticated:
    st.title("Welcome to LowKey")
    st.session_state.role = st.selectbox("I am a...", ["User", "Seller"])
    user = st.text_input("Username")
    if st.button("Enter"):
        st.session_state.authenticated = True
        st.rerun()
else:
    with st.sidebar:
        st.markdown("### Account")
        st.write(f"Logged in as: {st.session_state.role}")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()

    if st.session_state.role == "Seller":
        seller_page()
    else:
        home_page()
