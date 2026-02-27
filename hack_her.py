import streamlit as st
import pandas as pd
import difflib
from geopy.distance import geodesic
from datetime import datetime
import streamlit.components.v1 as components
import calendar

st.set_page_config(page_title="LowKey Deals", layout="wide", page_icon="✨")

# ==========================================================
# THEME
# ==========================================================
def apply_theme():
    st.markdown("""
    <style>
    html, body, [data-testid="stHeader"] { background-color:#FFFFFF; color:#000; }
    .deal-card {
        background:#FFF;
        padding:20px;
        border-radius:15px;
        border-top:4px solid #8B4513;
        margin-bottom:15px;
        box-shadow:0 4px 8px rgba(0,0,0,0.05);
        transition:0.3s;
    }
    .deal-card:hover {
        transform:translateY(-5px);
        box-shadow:0 8px 14px rgba(0,0,0,0.1);
    }
    .price-tag { color:#8B4513; font-weight:bold; font-size:1.3rem; }
    .badge {
        background:#FFE4B5;
        color:#8B4513;
        padding:4px 8px;
        font-size:0.7rem;
        border-radius:5px;
        font-weight:bold;
    }
    div.stButton > button {
        background:#8B4513 !important;
        color:white !important;
        border-radius:20px;
        font-weight:bold;
        transition:0.3s;
        width:100%;
    }
    div.stButton > button:hover {
        background:#A0522D !important;
        transform:scale(1.05);
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================================
# GLOBAL SHARED CATALOG (PERSISTENT)
# ==========================================================
@st.cache_resource
def get_global_catalog():
    return {}

GLOBAL_CATALOG = get_global_catalog()

def add_or_update_offer(product_name, offer):
    if product_name not in GLOBAL_CATALOG:
        GLOBAL_CATALOG[product_name] = []

    updated = False
    for i, existing in enumerate(GLOBAL_CATALOG[product_name]):
        if existing["seller_username"] == offer["seller_username"]:
            GLOBAL_CATALOG[product_name][i] = offer
            updated = True
            break

    if not updated:
        GLOBAL_CATALOG[product_name].append(offer)

# ==========================================================
# INITIAL DATA
# ==========================================================
def init_data():
    if "users" not in st.session_state:
        st.session_state.users = {"user1": "pass1"}

    if "sellers" not in st.session_state:
        st.session_state.sellers = {
            "seller1": {
                "password": "pass1",
                "store_name": "Appliance World",
                "loc": (9.95, 76.29),
                "open_hours": (9, 21),
                "open_days": list(calendar.day_name),
                "address": "123 Kochi St, Kerala"
            }
        }

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if "user_location" not in st.session_state:
        st.session_state.user_location = (9.9312, 76.2673)

# ==========================================================
# SELLER PAGE
# ==========================================================
def seller_page():
    st.title("📦 Manage Inventory")

    with st.form("add_product"):
        name = st.text_input("Product Name")
        desc = st.text_area("Description")
        price = st.number_input("Regular Price (₹)", min_value=0.0)
        sale_price = st.number_input("Sale Price (₹ optional)", min_value=0.0)

        submitted = st.form_submit_button("Add / Update Product")

        if submitted:
            if not name:
                st.error("Product name required")
                return

            store = st.session_state.store_info
            is_sale = sale_price > 0 and sale_price < price

            offer = {
                "seller_username": st.session_state.username,
                "store": store["store_name"],
                "address": store["address"],
                "loc": store["loc"],
                "price": price,
                "sale_price": sale_price if is_sale else None,
                "is_sale": is_sale,
                "desc": desc,
                "reviews": [],
                "open_hours": store["open_hours"],
                "open_days": store["open_days"]
            }

            add_or_update_offer(name, offer)
            st.success("Product Added/Updated Successfully 🎉")
            st.rerun()

# ==========================================================
# USER HOME PAGE
# ==========================================================
def user_home():
    st.title("✨ LowKey Deals")
    st.markdown("### Lowkey the best prices near you 💸")

    # Location
    st.subheader("📍 Your Location")
    with st.expander("Set manually"):
        lat = st.number_input("Latitude", value=st.session_state.user_location[0])
        lon = st.number_input("Longitude", value=st.session_state.user_location[1])
        if st.button("Save Location"):
            st.session_state.user_location = (lat, lon)
            st.success("Location Updated")

    st.divider()

    if not GLOBAL_CATALOG:
        st.info("No products available yet.")
        return

    search = st.text_input("🔍 Search Product")

    items = list(GLOBAL_CATALOG.keys())
    if search:
        items = difflib.get_close_matches(search, items, n=5, cutoff=0.4)

    for item in items:
        offers = GLOBAL_CATALOG[item]
        prices = [o["sale_price"] if o["is_sale"] else o["price"] for o in offers]
        min_price = min(prices)

        st.subheader(item)
        st.write(f"💰 Starting from ₹{min_price:,}")

        now = datetime.now()
        hour = now.hour
        day = now.strftime("%A")

        for o in offers:
            dist = geodesic(st.session_state.user_location, o["loc"]).km
            price = o["sale_price"] if o["is_sale"] else o["price"]
            is_open = day in o["open_days"] and o["open_hours"][0] <= hour < o["open_hours"][1]

            st.markdown("---")
            st.markdown(f"""
            <div class="deal-card">
                <h4>🏪 {o['store']}</h4>
                <div class="price-tag">₹{price:,}</div>
                <p>{o['desc']}</p>
                <small>📍 {o['address']}</small><br>
                <small>🚗 {dist:.1f} km away</small><br>
                <small>{'🟢 Open Now' if is_open else '🔴 Closed'}</small>
            </div>
            """, unsafe_allow_html=True)

# ==========================================================
# AUTH PAGE
# ==========================================================
def auth_page():
    st.title("Welcome to LowKey Deals")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        role = st.radio("I am a", ["User", "Seller"])
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if role == "User":
                if username in st.session_state.users and st.session_state.users[username] == password:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.role = "User"
                    st.rerun()
                else:
                    st.error("Invalid credentials")

            if role == "Seller":
                if username in st.session_state.sellers and st.session_state.sellers[username]["password"] == password:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.role = "Seller"
                    st.session_state.store_info = st.session_state.sellers[username]
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    with tab2:
        role = st.radio("Sign up as", ["User", "Seller"])
        username = st.text_input("Choose username")
        password = st.text_input("Choose password", type="password")

        if st.button("Create Account"):
            if role == "User":
                st.session_state.users[username] = password
                st.success("User created! Please login.")
            else:
                st.session_state.sellers[username] = {
                    "password": password,
                    "store_name": username,
                    "loc": (9.93, 76.27),
                    "open_hours": (9, 21),
                    "open_days": list(calendar.day_name),
                    "address": "Not set"
                }
                st.success("Seller created! Please login.")

# ==========================================================
# MAIN FLOW
# ==========================================================
apply_theme()
init_data()

if not st.session_state.authenticated:
    auth_page()
else:
    with st.sidebar:
        st.write(f"Welcome {st.session_state.username} 👋")

        if st.session_state.role == "Seller":
            page = st.radio("Menu", ["Home", "Manage Inventory"])
        else:
            page = "Home"

        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

    if page == "Manage Inventory":
        seller_page()
    else:
        user_home()
