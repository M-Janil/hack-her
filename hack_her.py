def apply_theme():
    st.markdown("""
        <style>
        /* Modern Sans Serif Font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
        
        html, body, [data-testid="stHeader"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, label {
            font-family: 'Inter', sans-serif;
            color: #1A1A1A !important;
        }

        /* Gradient Background for a premium feel */
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }

        /* The "Deal Card" styling */
        .deal-card {
            background-color: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            border-left: 5px solid #8B4513;
            transition: transform 0.3s ease;
        }
        .deal-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }

        /* Custom Button Styling */
        div.stButton > button {
            border-radius: 20px !important;
            background-color: #8B4513 !important;
            transition: 0.3s;
        }
        div.stButton > button:hover {
            background-color: #A0522D !important;
            border: 1px solid white !important;
        }
        </style>
    """, unsafe_allow_html=True)

def home_page():
    # Hero Section
    st.title("✨ LowKey Deals")
    st.subheader("Highkey savings on local appliances.")
    
    # Quick Stats/Trust Bar
    c1, c2, c3 = st.columns(3)
    c1.metric("Deals Found", "1,240", "+12 today")
    c2.metric("Top Discount", "45%", "Microwaves")
    c3.metric("Verified Sellers", "85", "Nearby")

    # Search Section with better UI
    with st.container():
        st.markdown("### 🔍 What are you hunting for?")
        search_input = st.text_input("", placeholder="Try 'Washing Machine'...", label_visibility="collapsed")
        
        if search_input:
            all_items = list(st.session_state.items.keys())
            suggestions = difflib.get_close_matches(search_input, all_items, n=3, cutoff=0.3)
            if suggestions:
                cols = st.columns(len(suggestions) + 1)
                cols[0].write("Suggestions:")
                for i, sug in enumerate(suggestions):
                    if cols[i+1].button(sug, key=f"sug_{sug}"):
                        st.session_state.selected_item = sug
                        st.rerun()

    st.divider()

    # Product Grid
    if 'selected_item' in st.session_state:
        # Detailed View
        item = st.session_state.items[st.session_state.selected_item]
        col_img, col_info = st.columns([1, 1])
        with col_img:
            # Placeholder for image
            st.image("https://via.placeholder.com/400x300.png?text=Product+Image", use_container_width=True)
        with col_info:
            st.header(st.session_state.selected_item)
            st.write(f"**Description:** {item['desc']}")
            st.markdown(f"## ₹{item['price']:,}")
            st.success("✅ In Stock - Pickup within 2 hours")
            if st.button("Reserve This Deal"):
                st.balloons()
                st.toast("Deal Reserved!")
            if st.button("⬅️ Back to Browse"):
                del st.session_state.selected_item
                st.rerun()
    else:
        # Trending Section
        st.markdown("### 🔥 Trending Near You")
        items = st.session_state.items
        
        # Create a grid using a loop and container styling
        cols = st.columns(3)
        for i, (name, info) in enumerate(items.items()):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="deal-card">
                    <p style="font-size: 0.8rem; color: #8B4513; font-weight: bold;">LOCAL DEAL</p>
                    <h4 style="margin: 0;">{name}</h4>
                    <p style="font-size: 0.9rem; color: #666;">{info['desc']}</p>
                    <p style="font-size: 1.2rem; font-weight: bold; color: #1A1A1A;">₹{info['price']:,}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"View {name}", key=f"btn_{name}"):
                    st.session_state.selected_item = name
                    st.rerun()
