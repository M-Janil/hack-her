import streamlit as st
import pandas as pd
import difflib
from geopy.distance import geodesic
from datetime import datetime
import calendar  # For day names

# --- CONFIGURATION ---
st.set_page_config(page_title="LowKey Deals", layout="wide", page_icon="🛍️")

# --- THEME: BROWN, BLACK, WHITE ---
def apply_theme():
    st.markdown("""
        <style>
        /* Global */
        .stApp { background-color: #FFFFFF; }
        h1, h2, h3, h4, h5, h6 { color: #8B4513; }
        p, label, .stMarkdown { color: #000000; }
        /* Buttons */
        div.stButton > button {
            background-color: #8B4513 !important;
            color: #FFFFFF !important;
            border-radius: 8px;
        }
        /* Inputs */
        input, textarea { border: 1px solid #8B4513 !important; }
        /* Cards */
        .item-card {
            background-color: #FFFFFF;
            border: 1px solid #8B4513;
            border-radius: 8px;
            padding: 10px;
            margin: 10px;
        }
        .sale-badge {
            background-color: #8B4513;
            color: #FFFFFF;
            padding: 5px;
            border-radius: 5px;
        }
        </style>
    """, unsafe_allow_html=True)

# --- DATA INITIALIZATION ---
def init_data():
    if 'item_offers' not in st.session_state:
        st.session_state.item_offers = {
            "Refrigerator": [
                {"store": "Store A", "address": "Address A, Kerala", "loc": (9.93, 76.27), "price": 15000, "sale_price": None, "is_sale": False, "desc": "Cool fridge", "reviews": [], "open_hours": (9, 21), "open_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]},
                {"store": "Store B", "address": "Address B, Kerala", "loc": (9.95, 76.29), "price": 16000, "sale_price": 14000, "is_sale": True, "desc": "Better fridge", "reviews": [], "open_hours": (10, 20), "open_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
            ],
            "Washing Machine": [
                {"store": "Store A", "address": "Address A, Kerala", "loc": (9.93, 76.27), "price": 12000, "sale_price": None, "is_sale": False, "desc": "Efficient washer", "reviews": [], "open_hours": (9, 21), "open_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]},
                {"store": "Store B", "address": "Address B, Kerala", "loc": (9.95, 76.29), "price": 13000, "sale_price": None, "is_sale": False, "desc": "Quiet washer", "reviews": [], "open_hours": (10, 20), "open_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
            ],
            "Microwave": [
                {"store": "Store C", "address": "Address C, Kerala", "loc": (9.94, 76.28), "price": 8000, "sale_price": 7000, "is_sale": True, "desc": "Quick heat", "reviews": [], "open_hours": (8, 22), "open_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]},
                {"store": "Store D", "address": "Address D, Kerala", "loc": (9.96, 76.30), "price": 8500, "sale_price": None, "is_sale": False, "desc": "Grill microwave", "reviews": [], "open_hours": (9, 21), "open_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]}
            ],
            "Air Conditioner": [
                {"store": "Store E", "address": "Address E, Kerala", "loc": (9.92, 76.26), "price": 25000, "sale_price": None, "is_sale": False, "desc": "Cool AC", "reviews": [], "open_hours": (10, 19), "open_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]},
                {"store": "Store F", "address": "Address F, Kerala", "loc": (9.97, 76.31), "price": 26000, "sale_price": 24000, "is_sale": True, "desc": "Inverter AC", "reviews": [], "open_hours": (9, 20), "open_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]}
            ],
            "Vacuum Cleaner": [
                {"store": "Store G", "address": "Address G, Kerala", "loc": (9.91, 76.25), "price": 5000, "sale_price": None, "is_sale": False, "desc": "Powerful vacuum", "reviews": [], "open_hours": (9, 21), "open_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]},
                {"store": "Store H", "address": "Address H, Kerala", "loc": (9.98, 76.32), "price": 5500, "sale_price": None, "is_sale": False, "desc": "Cordless vacuum", "reviews": [], "open_hours": (10, 22), "open_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
            ],
            "Blender": [
                {"store": "Store I", "address": "Address I, Kerala", "loc": (9.90, 76.24), "price": 3000, "sale_price": 2500, "is_sale": True, "desc": "High-speed blender", "reviews": [], "open_hours": (8, 20), "open_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]},
                {"store": "Store J", "address": "Address J, Kerala", "loc": (9.99, 76.33), "price": 3200, "sale_price": None, "is_sale": False, "desc": "Multi-function blender", "reviews": [], "open_hours": (9, 21), "open_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]}
            ]
        }  # Mock 6 items
    if 'users' not in st.session_state:
        st.session_state.users = {"user1": "pass1"}
    if 'sellers' not in st.session_state:
        st.session_state.sellers = {"seller1": "pass1"}
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_location' not in st.session_state:
        st.session_state.user_location = (9.93, 76.27)  # Default Kerala, IN

# --- LOGIN/SIGNUP PAGES ---
def auth_page():
    tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

    with tab_login:
        role = st.radio("Role", ["User", "Seller"])
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if role == "User" and username in st.session_state.users and st.session_state.users[username] == password:
                st.session_state.authenticated = True
                st.session_state.role = role
                st.session_state.username = username
                st.rerun()
            elif role == "Seller" and username in st.session_state.sellers and st.session_state.sellers[username] == password:
                st.session_state.authenticated = True
                st.session_state.role = role
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab_signup:
        role = st.radio("Role", ["User", "Seller"])
        username = st.text_input("New Username")
        password = st.text_input("New Password", type="password")
        if role == "Seller":
            store_name = st.text_input("Store Name")
            address = st.text_input("Store Address")
            lat = st.number_input("Latitude", value=9.93)
            lon = st.number_input("Longitude", value=76.27)
            open_from = st.number_input("Open From (hour)", value=9, min_value=0, max_value=23)
            open_to = st.number_input("Open To (hour)", value=21, min_value=0, max_value=23)
            open_days = st.multiselect("Open Days", options=list(calendar.day_name), default=list(calendar.day_name))
        if st.button("Sign Up"):
            if username in st.session_state.users or username in st.session_state.sellers:
                st.error("Username taken")
            elif role == "User":
                st.session_state.users[username] = password
                st.success("User created. Please login.")
            elif role == "Seller":
                if not store_name or not address or not open_days:
                    st.error("Missing seller details")
                else:
                    st.session_state.sellers[username] = password
                    # Store seller info in separate dict or integrate
                    st.session_state.seller_info = {"store_name": store_name, "address": address, "loc": (lat, lon), "open_hours": (open_from, open_to), "open_days": open_days}
                    st.success("Seller created. Please login.")
            else:
                st.error("Missing fields")

# --- HOME PAGE ---
def home_page():
    st.markdown("<h1 style='color: #8B4513;'>LowKey Deals</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #000000;'>Lowkey the best prices near you.</p>", unsafe_allow_html=True)

    # Location section only for users
    if st.session_state.role == "User":
        # Use query params for dynamic location
        params = st.experimental_get_query_params()
        if "lat" in params and "lon" in params:
            try:
                st.session_state.user_location = (float(params["lat"][0]), float(params["lon"][0]))
            except ValueError:
                pass
        # Display current location
        lat, lon = st.session_state.user_location
        st.write(f"Current location: Lat {lat}, Lon {lon}")

    # Sales section
    sales = [ (name, offer) for name, offers in st.session_state.item_offers.items() for offer in offers if offer["is_sale"]]
    if sales:
        st.subheader("Ongoing Sales")
        for name, offer in sales:
            st.markdown(f"<div class='sale-badge'>{name} at {offer['store']} for ₹{offer['sale_price']}</div>", unsafe_allow_html=True)

    # Grid of items
    st.subheader("Appliances")
    cols = st.columns(3)
    for i, name in enumerate(st.session_state.item_offers.keys()):
        with cols[i % 3]:
            min_price = min(offer["price"] for offer in st.session_state.item_offers[name])
            st.markdown(f"<div class='item-card'>{name} from ₹{min_price}</div>", unsafe_allow_html=True)
            # Placeholder image
            st.image("https://placehold.co/200x200", caption=name)

    # Logout
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

# --- SEARCH BAR (global after login) ---
def search_bar():
    search = st.text_input("Search for item")
    if search:
        suggestions = difflib.get_close_matches(search, st.session_state.item_offers.keys())
        if suggestions:
            with st.expander("Suggestions"):
                for sug in suggestions:
                    if st.button(sug):
                        st.session_state.selected_item = sug
                        st.rerun()

# --- ITEM DETAILS PAGE ---
def item_details_page(item_name):
    offers = st.session_state.item_offers[item_name]
    annotated = []
    for offer in offers:
        dist = geodesic(st.session_state.user_location, offer["loc"]).km
        avg_rating = sum(r["rating"] for r in offer["reviews"]) / len(offer["reviews"]) if offer["reviews"] else 0
        price = offer["sale_price"] if offer["is_sale"] else offer["price"]
        effort = (price / 100) + (dist * 0.5) + (5 - avg_rating)
        current_time = datetime.now()
        is_open = current_time.strftime("%A") in offer["open_days"] and offer["open_hours"][0] <= current_time.hour < offer["open_hours"][1]
        annotated.append({"offer": offer, "dist": dist, "avg_rating": avg_rating, "effort": effort, "is_open": is_open})

    annotated.sort(key=lambda x: x["effort"])
    for a in annotated:
        o = a["offer"]
        st.subheader(o["store"])
        st.write(f"Price: ₹{price} (Sale: {o['is_sale']})")
        st.write(f"Distance: {a['dist']} km")
        st.write(f"Rating: {a['avg_rating']}")
        st.write(f"Open: {a['is_open']}")
        st.write(f"Effort Score: {a['effort']}")
        # Reviews
        with st.expander("Reviews"):
            for r in o["reviews"]:
                st.write(f"{r['user']}: {r['rating']} stars - {r['text']}")
            # Add review
            if st.session_state.role == "User":
                with st.form("add_review"):
                    rating = st.radio("Rating", ["1 star", "2 stars", "3 stars", "4 stars", "5 stars"])
                    text = st.text_area("Review")
                    if st.form_submit_button("Submit"):
                        o["reviews"].append({"user": st.session_state.username, "rating": int(rating[0]), "text": text})
                        st.rerun()
        # Report purchase
        if st.session_state.role == "User":
            with st.form("report_purchase"):
                paid_price = st.number_input("Paid Price")
                bill = st.file_uploader("Upload Bill")
                if st.form_submit_button("Report"):
                    if bill:
                        # Mock verify
                        o["price"] = paid_price
                        st.success("Price updated after verification")

# --- SELLER MANAGE INVENTORY PAGE ---
def manage_inventory_page():
    st.subheader("Manage Inventory")
    # Form for new item
    with st.form("add_item"):
        name = st.text_input("Item Name")
        desc = st.text_area("Description")
        price = st.number_input("Price")
        sale_price = st.number_input("Sale Price (optional)")
        if st.form_submit_button("Add"):
            is_sale = bool(sale_price)
            offer = {
                "store": st.session_state.store_info["store_name"],  # From seller signup
                "address": st.session_state.store_info["address"],
                "loc": st.session_state.store_info["loc"],
                "price": price,
                "sale_price": sale_price if is_sale else None,
                "is_sale": is_sale,
                "desc": desc,
                "reviews": [],
                "open_hours": st.session_state.store_info["open_hours"],
                "open_days": st.session_state.store_info["open_days"]
            }
            if name not in st.session_state.item_offers:
                st.session_state.item_offers[name] = []
            st.session_state.item_offers[name].append(offer)
            st.success("Item added")

    # Bulk CSV
    csv_file = st.file_uploader("Upload CSV")
    if csv_file:
        df = pd.read_csv(csv_file)
        for _, row in df.iterrows():
            name = row["name"]
            desc = row["desc"]
            price = row["price"]
            sale_price = row.get("sale_price")
            is_sale = bool(sale_price)
            offer = {
                "store": st.session_state.store_info["store_name"],
                "address": st.session_state.store_info["address"],
                "loc": st.session_state.store_info["loc"],
                "price": price,
                "sale_price": sale_price if is_sale else None,
                "is_sale": is_sale,
                "desc": desc,
                "reviews": [],
                "open_hours": st.session_state.store_info["open_hours"],
                "open_days": st.session_state.store_info["open_days"]
            }
            if name not in st.session_state.item_offers:
                st.session_state.item_offers[name] = []
            st.session_state.item_offers[name].append(offer)
        st.success("CSV uploaded")

# --- MAIN EXECUTION ---
apply_theme()
init_data()

if not st.session_state.authenticated:
    auth_page()
else:
    with st.sidebar:
        st.title("Navigation")
        if st.session_state.role == "Seller":
            page = st.radio("Pages", ["Home", "Manage Inventory"])
        else:
            page = "Home"
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()

    search_bar()  # Global search

    if "selected_item" in st.session_state:
        item_details_page(st.session_state.selected_item)
    elif page == "Manage Inventory":
        manage_inventory_page()
    else:
        home_page()

# Assumptions:
# - Travel time proxy: distance * 0.5 (e.g., assuming 2 min per km or similar mock).
# - Bill verification: Mocked (always success, updates price).
# - Location: Only query params for dynamic; no JS button.
# - Seller info: Stored in session_state.store_info after signup/login.
# - Open status: Checks current day/hour.
# - Data sharing: session_state.item_offers shared between users/sellers.
# - More items mocked for 5+ requirement.
