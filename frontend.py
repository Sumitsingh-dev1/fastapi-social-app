import streamlit as st
import requests

API = "https://fastapi-social-app.onrender.com"

st.set_page_config(page_title="Social App 🚀", layout="wide")

# ---------------- STYLE ----------------
st.markdown("""
    <style>
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.title("🚀 Social App")
page = st.sidebar.radio("Navigate", ["Login", "Signup", "Feed", "Upload"])

# ---------------- LOGIN ----------------
if page == "Login":
    st.title("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        with st.spinner("Logging in..."):
            res = requests.post(
                f"{API}/auth/jwt/login",
                data={"username": email, "password": password}
            )

        if res.status_code == 200:
            st.session_state["token"] = res.json()["access_token"]
            st.success("✅ Logged in successfully")
        else:
            st.error("❌ Invalid credentials")

    if "token" in st.session_state:
        if st.button("Logout"):
            st.session_state.clear()
            st.success("Logged out")
            st.rerun()


# ---------------- SIGNUP ----------------
elif page == "Signup":
    st.title("📝 Create Account")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        with st.spinner("Creating account..."):
            res = requests.post(
                f"{API}/auth/register",
                json={"email": email, "password": password}
            )

        if res.status_code == 201:
            st.success("✅ Account created! Login now.")
        else:
            st.error("❌ Registration failed")


# ---------------- UPLOAD ----------------
elif page == "Upload":
    st.title("📤 Upload Post")

    if "token" not in st.session_state:
        st.warning("⚠️ Please login first")
    else:
        file = st.file_uploader("Upload Image/Video")
        caption = st.text_input("Write caption")

        if st.button("Upload"):
            if file is None:
                st.error("❌ Select a file")
            else:
                headers = {
                    "Authorization": f"Bearer {st.session_state['token']}"
                }

                with st.spinner("Uploading..."):
                    res = requests.post(
                        f"{API}/upload",
                        headers=headers,
                        files={"file": file},
                        data={"caption": caption}
                    )

                if res.status_code == 200:
                    st.success("✅ Uploaded successfully")
                    st.rerun()
                else:
                    st.error("❌ Upload failed")


# ---------------- FEED ----------------
elif page == "Feed":
    st.title("📰 Feed")

    if "token" not in st.session_state:
        st.warning("⚠️ Please login first")
    else:
        headers = {
            "Authorization": f"Bearer {st.session_state['token']}"
        }

        res = requests.get(f"{API}/feed", headers=headers)

        if res.status_code == 200:
            posts = res.json().get("posts", [])

            for post in posts:
                with st.container():

                    st.markdown(f"### 👤 {post['email']}")

                    # 🔥 IMAGE
                    st.image(post["url"])

                    # 🔥 CAPTION
                    st.write(post["caption"])

                    # 🔥 LIKE / DELETE SECTION
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        if st.button("❤️ Like", key=f"like_{post['id']}"):
                            requests.post(
                                f"{API}/posts/{post['id']}/like",
                                headers=headers
                            )
                            st.rerun()

                    with col2:
                        st.write(f"❤️ {post.get('likes', 0)}")

                    with col3:
                        if post["is_owner"]:
                            if st.button("🗑 Delete", key=f"del_{post['id']}"):
                                requests.delete(
                                    f"{API}/posts/{post['id']}",
                                    headers=headers
                                )
                                st.rerun()

                    # 🔥 COMMENT INPUT
                    comment = st.text_input("Add comment", key=f"c_{post['id']}")

                    if st.button("Post", key=f"btn_{post['id']}"):
                        requests.post(
                            f"{API}/posts/{post['id']}/comment",
                            headers=headers,
                            data={"content": comment}
                        )
                        st.rerun()

                    # 🔥 SHOW COMMENTS
                    for c in post.get("comments", []):
                        st.write(f"💬 {c['content']}")

                    st.markdown("---")

        else:
            st.error(res.text)