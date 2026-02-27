import streamlit as st
import difflib
from geopy.distance import geodesic
from datetime import datetime
import calendar

st.set_page_config(page_title="LowKey Deals", layout="wide", page_icon="✨")

# ==========================================================
# THEME
# ==========================================================
def apply_theme():
    st.markdown("""
    <style>
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
    .price-tag { color:#8B4513; font-weight:bold; font-size:1.2rem; }
    div.stButton > button {
        background:#8B4513 !important;
        color:white !important;
        border-radius:20px;
        font-weight:bold;
        width:100%;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================================
# GLOBAL SHARED CATALOG
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

def sync_seller_store_updates(username):
    if username not in st.session_state.sellers:
        return

    store = st.session_state.sellers[username]

    for product, offers in GLOBAL_CATALOG.items():
        for offer in offers:
            if offer["seller_username"] == username:
                offer["store"] = store["store_name"]
                offer["address"] = store["address"]
                offer["loc"] = store["loc"]
                offer["open_hours"] = store["open_hours"]
                offer["open_days"] = store["open_days"]

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

    store = st.session_state.store_info

    st.subheader("Update Store Info")

    with st.form("update_store"):
        store_name = st.text_input("Store Name", value=store["store_name"])
        address = st.text_input("Address", value=store["address"])
        lat = st.number_input("Latitude", value=store["loc"][0])
        lon = st.number_input("Longitude", value=store["loc"][1])
        open_hour = st.number_input("Opens at", 0, 23, store["open_hours"][0])
        close_hour = st.number_input("Closes at", 0, 23, store["open_hours"][1])
        open_days = st.multiselect(
            "Open Days",
            list(calendar.day_name),
            default=store["open_days"]
        )

        if st.form_submit_button("Update Store Info"):
            st.session_state.sellers[st.session_state.username] = {
                "password": store["password"],
                "store_name": store_name,
                "address": address,
                "loc": (lat, lon),
                "open_hours": (open_hour, close_hour),
                "open_days": open_days
            }

            st.session_state.store_info = st.session_state.sellers[st.session_state.username]
            sync_seller_store_updates(st.session_state.username)

            st.success("Store info updated and synced!")

    st.divider()
    st.subheader("Add / Update Product")

    with st.form("add_product"):
        name = st.text_input("Product Name")
        desc = st.text_area("Description")
        price = st.number_input("Regular Price (₹)", min_value=0.0)
        sale_price = st.number_input("Sale Price (₹ optional)", min_value=0.0)

        if st.form_submit_button("Add / Update Product"):
            if not name:
                st.error("Product name required")
                return

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
            sync_seller_store_updates(st.session_state.username)

            st.success("Product added/updated successfully!")
            st.rerun()

# ==========================================================
# USER HOME PAGE
# ==========================================================
def user_home():
    st.title("✨ LowKey Deals")
    st.write("Lowkey the best prices near you 💸")

    if not GLOBAL_CATALOG:
        st.info("No products available yet.")
        return

    search = st.text_input("🔍 Search Product")
    items = list(GLOBAL_CATALOG.keys())

    if search:
        items = difflib.get_close_matches(search, items, n=5, cutoff=0.4)

    for item in items:
        st.subheader(item)
        offers = GLOBAL_CATALOG[item]

        prices = [o["sale_price"] if o["is_sale"] else o["price"] for o in offers]
        min_price = min(prices)

        st.write(f"💰 Starting from ₹{min_price:,}")

        now = datetime.now()
        hour = now.hour
        day = now.strftime("%A")

        for o in offers:
            dist = geodesic(st.session_state.user_location, o["loc"]).km
            price = o["sale_price"] if o["is_sale"] else o["price"]
            is_open = day in o["open_days"] and o["open_hours"][0] <= hour < o["open_hours"][1]

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

    role = st.radio("Login As", ["User", "Seller"])
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
