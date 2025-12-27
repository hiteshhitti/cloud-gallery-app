import streamlit as st
import cloudinary
import cloudinary.api
from cloudinary.search import Search
import os


# ================= PAGE CONFIG =================
st.set_page_config(layout="wide")
st.title("☁️ My Cloud Gallery")

# ================= CLOUDINARY CONFIG =================
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

ROOT_FOLDER = "mygallery"   # ⚠️ EXACT same naam Cloudinary folder ka

# ================= SESSION STATE =================
if "current_album" not in st.session_state:
    st.session_state.current_album = None

if "fullscreen_image" not in st.session_state:
    st.session_state.fullscreen_image = None

# ================= HELPERS =================
def get_albums():
    try:
        res = cloudinary.api.subfolders(ROOT_FOLDER)
        return [f["name"] for f in res.get("folders", [])]
    except Exception as e:
        st.error(f"Album fetch error: {e}")
        return []

# def get_images(album):
#     images = []
#     next_cursor = None

#     while True:
#         res = cloudinary.api.resources(
#             type="upload",
#             resource_type="image",                 # 🔥 MUST
#             prefix=f"{ROOT_FOLDER}/{album}/",      # 🔥 trailing slash
#             max_results=100,
#             next_cursor=next_cursor
#         )

#         for r in res.get("resources", []):
#             images.append(r["secure_url"])

#         next_cursor = res.get("next_cursor")
#         if not next_cursor:
#             break

#     return images

def get_images(album):
    images = []
    next_cursor = None

    while True:
        search = Search().expression(
            f"folder:{ROOT_FOLDER}/{album}"
        ).sort_by(
            "created_at", "desc"
        ).max_results(
            100
        )

        if next_cursor:
            search = search.next_cursor(next_cursor)

        result = search.execute()

        for r in result.get("resources", []):
            images.append(r["secure_url"])

        next_cursor = result.get("next_cursor")
        if not next_cursor:
            break

    return images



# ================= FULLSCREEN VIEW =================
if st.session_state.fullscreen_image:
    if st.button("❌ Close Image"):
        st.session_state.fullscreen_image = None
        st.rerun()

    st.image(st.session_state.fullscreen_image, use_container_width=True)

# ================= ALBUM VIEW =================
elif st.session_state.current_album is None:
    st.subheader("📂 Albums")

    albums = get_albums()

    if not albums:
        st.warning("No albums found. Check folder structure in Cloudinary.")

    cols = st.columns(4)
    for i, album in enumerate(albums):
        with cols[i % 4]:
            if st.button(f"📁 {album}"):
                st.session_state.current_album = album
                st.rerun()

# ================= IMAGE GRID VIEW =================
else:
    album = st.session_state.current_album
    st.subheader(f"🖼️ {album}")

    if st.button("⬅ Back to Albums"):
        st.session_state.current_album = None
        st.rerun()

    images = get_images(album)

    if not images:
        st.warning("No images found in this album")

    cols = st.columns(5)
    for i, img_url in enumerate(images):
        with cols[i % 5]:
            st.image(img_url, use_container_width=True)
            if st.button("🔍 View", key=img_url):
                st.session_state.fullscreen_image = img_url
                st.rerun()
