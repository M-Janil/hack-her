import streamlit as st
import pandas as pd
import difflib
from geopy.distance import geodesic
from datetime import datetime
import streamlit.components.v1 as components
import calendar

# --- CONFIGURATION ---
st.set_page_config(page_title="LowKey Deals", layout="wide", page_icon="✨")

# --- 1. THEME: BROWN, BLACK, WHITE WITH LIVELINESS ---
def apply_theme():
    st.markdown("""
        <style>
        /* Global Text & Label Colors */
        html, body, [data-testid="stHeader"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, label, span, .stRadio p {
            color: #000000 !important;
            font-weight: 500;
        }
        .stApp { background-color: #FFFFFF; }
        /* Enhanced Card Styling with Hover Animation */
        .deal-card {
            background-color: #FFFFFF;
            padding: 20px;
            border-radius: 15px;
            border-top: 4px solid #8B4513;
            margin-bottom: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: transform 0.3s ease-in-out, box-shadow 0.3s;
        }
        .deal-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.1);
        }
        .price-tag {
            color: #8B4513;
            font-size: 1.4rem;
            font-weight: bold;
        }
        /* Status Badge with Pulse Animation */
        .badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: bold;
            text-transform: uppercase;
            background-color: #FFE4B5;
            color: #8B4513;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        input {
            color: #000000 !important;
            background-color: #FFFFFF !important;
            border: 2px solid #8B4513 !important;
        }
        div.stButton > button {
            background-color: #8B4513 !important;
            color: #FFFFFF !important;
            border-radius: 20px;
            font-weight: bold;
            transition: 0.3s;
            width: 100%;
        }
        div.stButton > button:hover {
            background-color: #A0522D !important;
            transform: scale(1.05);
        }
        </style>
    """, unsafe_allow_html=True)

# --- 2. DATA INITIALIZATION ---
def init_data():
    if 'item_offers' not in st.session_state or not isinstance(st.session_state.item_offers, dict):
        st.session_state.item_offers = {
            "Refrigerator": [
                {
                    "seller_username": "seller1",
                    "store": "Appliance World",
                    "address": "123 Kochi St, Kerala",
                    "loc": (9.95, 76.29),
                    "price": 25000,
                    "sale_price": None,
                    "is_sale": False,
                    "desc": "Double door, 250L",
                    "reviews": [{"user": "user1", "rating": 4, "text": "Good product"}],
                    "open_hours": (9, 21),
                    "open_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
                },
                {
                    "seller_username": "seller2",
                    "store": "Home Mart",
                    "address": "456 Ernakulam Rd, Kerala",
                    "loc": (9.93, 76.27),
                    "price": 26000,
                    "sale_price": 24000,
                    "is_sale": True,
                    "desc": "Double door, 260L",
                    "reviews": [],
                    "open_hours": (10, 22),
                    "open_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                }
            ],
            "Washing Machine": [
                {
                    "seller_username": "seller1",
                    "store": "Appliance World",
                    "address": "123 Kochi St, Kerala",
                    "loc": (9.95, 76.29),
                    "price": 18000,
                    "sale_price": None,
                    "is_sale": False,
                    "desc": "Front load, 7kg",
                    "reviews": [],
                    "open_hours": (9, 21),
                    "open_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
                },
                {
                    "seller_username": "seller2",
                    "store": "Home Mart",
                    "address": "456 Ernakulam Rd, Kerala",
                    "loc": (9.93, 76.27),
                    "price": 17000,
                    "sale_price": None,
                    "is_sale": False,
                    "desc": "Front load, 6kg",
                    "reviews": [{"user": "user1", "rating": 5, "text": "Excellent"}],
                    "open_hours": (10, 22),
                    "open_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                }
            ]
        }

    if 'users' not in st.session_state:
        st.session_state.users = {"user1": "pass1"}

    if 'sellers' not in st.session_state:
        st.session_state.sellers = {
            "seller1": {
                "password": "pass1",
                "store_name": "Appliance World",
                "loc": (9.95, 76.29),
                "open_hours": (9, 21),
                "open_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
                "address": "123 Kochi St, Kerala"
            },
            "seller2": {
                "password": "pass2",
                "store_name": "Home Mart",
                "loc": (9.93, 76.27),
                "open_hours": (10, 22),
                "open_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                "address": "456 Ernakulam Rd, Kerala"
            }
        }

    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if 'user_location' not in st.session_state:
        st.session_state.user_location = (9.9312, 76.2673)  # Kochi, Kerala (default)

    if 'role' not in st.session_state:
        st.session_state.role = None

# --- Helper to force refresh catalog ---
def refresh_catalog():
    if 'catalog_version' not in st.session_state:
        st.session_state.catalog_version = 0
    st.session_state.catalog_version += 1

# --- 3. SELLER INVENTORY MANAGEMENT PAGE ---
def admin_page():
    st.title("📦 Manage Inventory")
    
    if 'store_info' not in st.session_state or not st.session_state.store_info:
        st.error("Store information not found. Please log out and log in again.")
        return

    store_name = st.session_state.store_info["store_name"]
    st.subheader(f"Your store: {store_name}")

    with st.expander("💡 CSV Format Instructions"):
        st.write("Columns: `name`, `desc`, `price`, `sale_price` (optional)")

    uploaded_file = st.file_uploader("Bulk Upload via CSV", type="csv")
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            added_count = 0
            for _, row in df.iterrows():
                name = str(row['name']).strip()
                desc = str(row.get('desc', '')).strip()
                price = float(row['price'])
                sale_price = float(row.get('sale_price', 0))
                is_sale = sale_price > 0 and sale_price < price

                offer = {
                    "seller_username": st.session_state.username,
                    "store": store_name,
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

                # Replace existing offer from THIS seller only
                updated = False
                for i, existing in enumerate(st.session_state.item_offers[name]):
                    if existing.get("seller_username") == st.session_state.username:
                        st.session_state.item_offers[name][i] = offer
                        updated = True
                        break
                if not updated:
                    st.session_state.item_offers[name].append(offer)
                added_count += 1

            refresh_catalog()
            st.success(f"Imported/Updated {added_count} items!")
        except Exception as e:
            st.error(f"Error processing CSV: {e}")

    st.divider()
    st.subheader("Add / Update Single Item")

    with st.form("manual_add"):
        col1, col2 = st.columns(2)
        name = col1.text_input("Product Name", key="add_name")
        price = col2.number_input("Regular Price (₹)", min_value=0.0, step=100.0)
        sale_price = col2.number_input("Sale Price (optional, ₹)", min_value=0.0, step=100.0)
        desc = st.text_area("Description")

        submitted = st.form_submit_button("Add / Update Item")
        if submitted and name.strip():
            is_sale = sale_price > 0 and sale_price < price
            offer = {
                "seller_username": st.session_state.username,
                "store": store_name,
                "address": st.session_state.store_info["address"],
                "loc": st.session_state.store_info["loc"],
                "price": price,
                "sale_price": sale_price if is_sale else None,
                "is_sale": is_sale,
                "desc": desc.strip(),
                "reviews": [],
                "open_hours": st.session_state.store_info["open_hours"],
                "open_days": st.session_state.store_info["open_days"]
            }

            if name not in st.session_state.item_offers:
                st.session_state.item_offers[name] = []

            updated = False
            for i, existing in enumerate(st.session_state.item_offers[name]):
                if existing.get("seller_username") == st.session_state.username:
                    st.session_state.item_offers[name][i] = offer
                    updated = True
                    break
            if not updated:
                st.session_state.item_offers[name].append(offer)

            refresh_catalog()
            st.success(f"Item '{name}' added/updated successfully!")
        elif submitted:
            st.error("Product name is required.")

# --- 4. USER BROWSING PAGE (only for regular users) ---
def home_page():
    # ── Location input ───────────────────────────────────────
    st.subheader("🗺️ Your Location")
    st.write("Share your location for accurate distance calculation")

    components.html("""
        <button onclick="getLocation()" style="background:#8B4513;color:white;padding:10px 20px;border:none;border-radius:20px;cursor:pointer;">
            Get My Location
        </button>
        <script>
        function getLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(showPosition, showError);
            } else {
                alert("Geolocation not supported.");
            }
        }
        function showPosition(position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            const url = new URL(window.parent.location);
            url.searchParams.set('lat', lat);
            url.searchParams.set('lon', lon);
            window.parent.location = url;
        }
        function showError(error) {
            alert("Location error: " + error.message);
        }
        </script>
    """, height=70)

    # Read from URL params
    query_params = st.query_params
    if 'lat' in query_params and 'lon' in query_params:
        try:
            lat = float(query_params['lat'][0])
            lon = float(query_params['lon'][0])
            st.session_state.user_location = (lat, lon)
            st.success(f"Location updated: {lat:.5f}, {lon:.5f}")
        except:
            st.warning("Could not parse location from URL.")

    with st.expander("Set location manually"):
        lat = st.number_input("Latitude", value=st.session_state.user_location[0], step=0.0001)
        lon = st.number_input("Longitude", value=st.session_state.user_location[1], step=0.0001)
        if st.button("Save manual location"):
            st.session_state.user_location = (lat, lon)
            st.success("Location saved!")

    st.divider()

    # ── Main content ─────────────────────────────────────────
    col_title, col_loc = st.columns([4, 1])
    with col_title:
        st.title("✨ LowKey Deals")
        st.markdown("### Find the best local appliance prices near you 🛒💸")
    with col_loc:
        st.caption("📍 Your location")
        st.code(f"{st.session_state.user_location[0]:.4f}, {st.session_state.user_location[1]:.4f}")

    # ── Sales highlight ──────────────────────────────────────
    st.subheader("🔥 Hot Sales Right Now")
    sales = []
    for item, offers in st.session_state.item_offers.items():
        for o in offers:
            if o.get("is_sale", False):
                sales.append((item, o))

    if sales:
        cols = st.columns(3)
        for i, (name, o) in enumerate(sales):
            dist = geodesic(st.session_state.user_location, o["loc"]).km
            with cols[i % 3]:
                st.markdown(f"""
                <div class="deal-card">
                    <span class="badge">SALE 🔥</span>
                    <h4>{name}</h4>
                    <p>{o['desc'][:60]}{'...' if len(o['desc']) > 60 else ''}</p>
                    <del>₹{o['price']:,}</del> <span class="price-tag">₹{o['sale_price']:,}</span>
                    <div style="font-size:0.85rem;color:#666;margin-top:8px;">≈ {dist:.1f} km</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("View", key=f"sale_view_{i}_{name}"):
                    st.session_state.selected_item = name
                    st.rerun()
    else:
        st.info("No active sales at the moment. Check back soon! 😊")

    # ── Search ───────────────────────────────────────────────
    search_term = st.text_input("🔍 Search appliances...", placeholder="e.g. Refrigerator, Washing Machine")
    if search_term:
        all_names = list(st.session_state.item_offers.keys())
        matches = difflib.get_close_matches(search_term, all_names, n=5, cutoff=0.5)
        if matches:
            st.write("Suggestions:")
            cols = st.columns(min(5, len(matches)))
            for i, match in enumerate(matches):
                if cols[i].button(match, key=f"suggest_{i}"):
                    st.session_state.selected_item = match
                    st.rerun()

    st.divider()

    # ── Selected item detail ─────────────────────────────────
    if 'selected_item' in st.session_state:
        name = st.session_state.selected_item
        offers = st.session_state.item_offers.get(name, [])

        if offers:
            st.header(f"🛍️ {name}")
            user_loc = st.session_state.user_location
            now = datetime.now()
            hour = now.hour
            day = now.strftime("%A")

            prices = [o["sale_price"] if o.get("is_sale") else o["price"] for o in offers]
            min_price = min(prices) if prices else 0
            lowest = next((o["store"] for o in offers if (o["sale_price"] if o.get("is_sale") else o["price"]) == min_price), "—")

            st.info(f"Best price found: **{lowest}**  ₹{min_price:,} 💰")

            annotated = []
            for o in offers:
                dist = geodesic(user_loc, o["loc"]).km
                reviews = o.get("reviews", [])
                avg = sum(r["rating"] for r in reviews) / len(reviews) if reviews else 0
                current_price = o["sale_price"] if o.get("is_sale") else o["price"]
                price_score = (current_price - min_price) / (max(prices) - min_price) if max(prices) > min_price else 0
                effort = price_score * 50 + dist * 0.6 + (5 - avg) * 3
                is_open = day in o["open_days"] and o["open_hours"][0] <= hour < o["open_hours"][1]

                annotated.append({
                    "offer": o,
                    "dist": dist,
                    "avg_rating": avg,
                    "effort": effort,
                    "is_open": is_open
                })

            annotated.sort(key=lambda x: x["effort"])

            for entry in annotated:
                o = entry["offer"]
                st.subheader(f"🏪 {o['store']}")
                st.write(f"**Address:** {o['address']}")
                price_str = f"₹{o['sale_price']:,} (Sale!)" if o.get("is_sale") else f"₹{o['price']:,}"
                st.metric("Price", price_str)
                st.write(f"Distance: **{entry['dist']:.1f} km**")
                st.write(f"Rating: **{entry['avg_rating']:.1f}** ⭐" if entry['avg_rating'] > 0 else "No ratings yet")
                st.write("**Open now** ✅" if entry["is_open"] else "**Closed** ❌")
                st.write(f"Open: {', '.join(o['open_days'])}  |  {o['open_hours'][0]}–{o['open_hours'][1]}")

                img_url = f"https://loremflickr.com/320/180/appliance,{name.lower().replace(' ','')}"
                st.image(img_url, use_column_width=True)

                maps_link = f"https://www.google.com/maps/dir/?api=1&origin={user_loc[0]},{user_loc[1]}&destination={o['loc'][0]},{o['loc'][1]}"
                st.markdown(f"[🗺️ Get Directions]({maps_link})")

                with st.expander("Reviews"):
                    if o.get("reviews"):
                        for r in o["reviews"]:
                            st.write(f"**{r['user']}**: {r['rating']} ⭐ – {r['text']}")
                    else:
                        st.write("No reviews yet.")

                    if st.session_state.role == "User":
                        with st.form(f"review_{o['store']}_{name}"):
                            rating_str = st.radio("Your rating", ["1 ⭐","2 ⭐⭐","3 ⭐⭐⭐","4 ⭐⭐⭐⭐","5 ⭐⭐⭐⭐⭐"], horizontal=True)
                            rating = int(rating_str[0])
                            comment = st.text_area("Your comment")
                            if st.form_submit_button("Submit Review"):
                                o["reviews"].append({
                                    "user": st.session_state.username,
                                    "rating": rating,
                                    "text": comment
                                })
                                st.success("Review submitted!")
                                st.rerun()

            if st.button("← Back to all items"):
                del st.session_state.selected_item
                st.rerun()

        else:
            st.warning("No offers found for this product.")

    else:
        # Grid view of all products
        st.subheader("🛒 Available Appliances")
        items = list(st.session_state.item_offers.keys())
        if not items:
            st.info("No products in catalog yet. Sellers can add items in 'Manage Inventory'.")
        else:
            cols = st.columns(3)
            for i, name in enumerate(items):
                offers = st.session_state.item_offers[name]
                prices = [o["sale_price"] if o.get("is_sale") else o["price"] for o in offers]
                min_p = min(prices) if prices else 0
                min_d = min(geodesic(st.session_state.user_location, o["loc"]).km for o in offers) if offers else 999

                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="deal-card">
                        <h4>{name}</h4>
                        <p class="price-tag">From ₹{min_p:,}</p>
                        <div style="color:#666;font-size:0.9rem;">Closest ≈ {min_d:.1f} km</div>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("View offers", key=f"view_{i}_{name}"):
                        st.session_state.selected_item = name
                        st.rerun()

# --- 5. AUTHENTICATION PAGE ---
def auth_page():
    st.title("Welcome to LowKey Deals")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        role = st.radio("I am a", ["User", "Seller"], key="login_role")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            if not (username and password):
                st.error("Please enter username and password.")
            elif role == "User":
                if username in st.session_state.users and st.session_state.users[username] == password:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.role = "User"
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
            elif role == "Seller":
                if username in st.session_state.sellers and st.session_state.sellers[username]["password"] == password:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.role = "Seller"
                    st.session_state.store_info = st.session_state.sellers[username]
                    st.rerun()
                else:
                    st.error("Invalid credentials.")

    with tab2:
        role = st.radio("Sign up as", ["User", "Seller"], key="signup_role")
        username = st.text_input("Choose username", key="signup_user")
        password = st.text_input("Choose password", type="password", key="signup_pass")

        store_info = {}
        if role == "Seller":
            store_info["store_name"] = st.text_input("Store Name")
            store_info["address"] = st.text_input("Store Address")
            store_info["loc"] = (
                st.number_input("Store Latitude", value=9.93),
                st.number_input("Store Longitude", value=76.27)
            )
            store_info["open_hours"] = (
                st.number_input("Opens at (hour)", 0, 23, 9),
                st.number_input("Closes at (hour)", 0, 23, 21)
            )
            store_info["open_days"] = st.multiselect(
                "Open days",
                list(calendar.day_name),
                default=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
            )

        if st.button("Sign Up"):
            if not (username and password):
                st.error("Username and password required.")
            elif role == "User":
                if username in st.session_state.users:
                    st.error("Username already taken.")
                else:
                    st.session_state.users[username] = password
                    st.success("Account created! Please log in.")
            elif role == "Seller":
                if username in st.session_state.sellers:
                    st.error("Username already taken.")
                elif not all([store_info.get(k) for k in ["store_name","address","open_days"]]):
                    st.error("Please fill all store details.")
                else:
                    st.session_state.sellers[username] = {
                        "password": password,
                        **store_info
                    }
                    st.success("Seller account created! Please log in.")

# --- MAIN EXECUTION FLOW ---
apply_theme()
init_data()

if not st.session_state.authenticated:
    auth_page()
else:
    with st.sidebar:
        st.markdown(f"**Welcome, {st.session_state.username}** 👋")
        st.caption(f"Role: {st.session_state.role}")

        if st.session_state.role == "Seller":
            page = st.radio("Menu", ["Manage Inventory"])
        else:
            page = st.radio("Menu", ["Home"])

        st.divider()
        if st.button("Logout"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    if st.session_state.role == "User" and page == "Home":
        home_page()
    elif st.session_state.role == "Seller" and page == "Manage Inventory":
        admin_page()
    else:
        st.info("Please select an option from the sidebar.")
