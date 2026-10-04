"""
Nest — My HTML App Hub
Built by: Gesner Deslandes — Software Engineer
Contact: (509)-47385663 · deslandes78@gmail.com
"""

import base64
import json
import re
import shutil
from pathlib import Path

import streamlit as st

# =================== CONFIG ===================
YOUR_NAME    = "GESNER DESLANDES"
YOUR_TITLE   = "SOFTWARE ENGINEER"
YOUR_PHONE   = "(509)-47385663"
YOUR_EMAIL   = "deslandes78@gmail.com"
APP_NAME     = "NEST — MY HTML HUB"
APPS_DIR     = Path("apps")
URLS_FILE    = Path("url_apps.json")
PROFILE_DIR  = Path("profile")
# ==============================================

APPS_DIR.mkdir(exist_ok=True)
PROFILE_DIR.mkdir(exist_ok=True)

st.set_page_config(
    page_title=f"{APP_NAME} · {YOUR_NAME}",
    page_icon="🪺",
    layout="wide",
)


# ---------------- Light blue global styling ----------------
st.markdown(
    """
    <style>
      .stApp {
        background: linear-gradient(180deg, #e0f2fe 0%, #f0f9ff 100%);
      }
      section[data-testid="stSidebar"] { background-color: #bae6fd; }

      .stButton > button {
        background-color: #0284c7 !important;
        color: #ffffff !important;
        border: 0 !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: background 0.15s ease !important;
      }
      .stButton > button:hover { background-color: #0369a1 !important; }

      div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #f0f9ff;
        border: 1px solid #7dd3fc !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 14px rgba(2, 132, 199, 0.08);
      }
      details {
        background-color: #f0f9ff;
        border: 1px solid #7dd3fc !important;
        border-radius: 12px !important;
      }
      input, textarea {
        background-color: #ffffff !important;
        border: 1px solid #7dd3fc !important;
        border-radius: 10px !important;
      }
      input:focus, textarea:focus {
        border-color: #0284c7 !important;
        box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.18) !important;
      }
      hr { border-color: #bae6fd !important; }
      h2, h3 { color: #0c4a6e; }

      .badge {
        display:inline-block; padding:2px 10px; border-radius:999px;
        font-size:0.72rem; font-weight:700; letter-spacing:0.05em;
      }
      .badge-file { background:#bae6fd; color:#075985; }
      .badge-url  { background:#c7d2fe; color:#3730a3; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------- Helpers ----------------
def safe_name(raw: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_\- ]", "", raw).strip()
    return cleaned.replace(" ", "-") or "app"


def load_url_apps():
    if URLS_FILE.exists():
        try:
            data = json.loads(URLS_FILE.read_text())
            if isinstance(data, list):
                return data
        except Exception:
            pass
    return []


def save_url_apps(items):
    try:
        URLS_FILE.write_text(json.dumps(items, indent=2))
    except Exception as e:
        st.warning(f"Could not save URL list: {e}")


def list_local_apps():
    apps = []
    for entry in sorted(APPS_DIR.iterdir(), key=lambda p: p.name.lower()):
        if entry.name.startswith("."):
            continue
        if entry.is_dir():
            index = entry / "index.html"
            if not index.exists():
                htmls = sorted(entry.glob("*.html"))
                if not htmls:
                    continue
                index = htmls[0]
            apps.append({
                "title": entry.name.replace("-", " ").replace("_", " ").title(),
                "path": index,
                "key": entry.name,
                "kind": "file",
            })
        elif entry.suffix.lower() == ".html":
            apps.append({
                "title": entry.stem.replace("-", " ").replace("_", " ").title(),
                "path": entry,
                "key": entry.name,
                "kind": "file",
            })
    return apps


def list_url_apps():
    return [
        {
            "title": u.get("title", "Untitled"),
            "url":   u.get("url", ""),
            "key":   u.get("key", safe_name(u.get("title", "url-app"))),
            "kind":  "url",
        }
        for u in load_url_apps()
    ]


def list_all_apps():
    return list_local_apps() + list_url_apps()


# ---------------- Profile picture helpers ----------------
PROFILE_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".gif")


def get_profile_path():
    """Return the path to the current profile picture, or None."""
    for f in sorted(PROFILE_DIR.iterdir()):
        if f.suffix.lower() in PROFILE_EXTS and f.is_file():
            return f
    return None


def get_profile_base64():
    """Return (base64_string, mime) or (None, None)."""
    p = get_profile_path()
    if not p:
        return None, None
    mime = {
        ".png": "image/png", ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg", ".webp": "image/webp", ".gif": "image/gif",
    }.get(p.suffix.lower(), "image/png")
    return base64.b64encode(p.read_bytes()).decode(), mime


def save_profile(uploaded_file):
    """Save the uploaded image, replacing any previous one."""
    for f in PROFILE_DIR.iterdir():
        if f.is_file() and f.suffix.lower() in PROFILE_EXTS:
            f.unlink()
    ext = Path(uploaded_file.name).suffix.lower()
    if ext not in PROFILE_EXTS:
        ext = ".png"
    (PROFILE_DIR / f"avatar{ext}").write_bytes(uploaded_file.read())


def delete_profile():
    for f in PROFILE_DIR.iterdir():
        if f.is_file() and f.suffix.lower() in PROFILE_EXTS:
            f.unlink()


# ---------------- Session state ----------------
if "active_app" not in st.session_state:
    st.session_state.active_app = None
if "show_profile_uploader" not in st.session_state:
    st.session_state.show_profile_uploader = False


# ---------------- Header with profile picture ----------------
avatar_b64, avatar_mime = get_profile_base64()

if avatar_b64:
    avatar_html = f"""
        <img src="data:{avatar_mime};base64,{avatar_b64}"
             alt="{YOUR_NAME}"
             style="
                width:130px; height:130px; object-fit:cover;
                border-radius:50%;
                border:4px solid #0284c7;
                box-shadow:0 6px 18px rgba(2,132,199,.25);
                display:block;
             ">
    """
else:
    initials = "".join([w[0] for w in YOUR_NAME.split()[:2]]).upper()
    avatar_html = f"""
        <div style="
            width:130px; height:130px; border-radius:50%;
            border:4px solid #0284c7;
            background:#bae6fd; color:#075985;
            display:flex; align-items:center; justify-content:center;
            font-size:2.4rem; font-weight:800;
            box-shadow:0 6px 18px rgba(2,132,199,.25);
        ">{initials}</div>
    """

# --- Header block ---
st.markdown(
    f"""
    <div style="
        display:flex; align-items:center; gap:26px;
        padding: 28px 30px;
        background: linear-gradient(135deg, #bae6fd 0%, #e0f2fe 100%);
        border: 1px solid #7dd3fc;
        border-radius: 18px;
        box-shadow: 0 8px 24px rgba(2, 132, 199, 0.12);
        margin-bottom: 8px;
    ">
        <div>{avatar_html}</div>
        <div style="flex:1; min-width:0;">
            <h1 style="
                margin:0; font-size:2.7rem; font-weight:800;
                letter-spacing:-0.02em;
                background: linear-gradient(90deg,#0369a1,#0284c7);
                -webkit-background-clip: text; background-clip: text;
                color: transparent;
            ">{YOUR_NAME}</h1>
            <p style="
                margin:6px 0 0; font-size:0.98rem; font-weight:600;
                letter-spacing:0.14em; color:#075985; text-transform:uppercase;
            ">{YOUR_TITLE}</p>
            <p style="margin:8px 0 0; font-size:0.92rem; color:#0c4a6e;">
                📞 {YOUR_PHONE} &nbsp;·&nbsp; ✉️
                <a href="mailto:{YOUR_EMAIL}" style="color:#0284c7; text-decoration:none;">{YOUR_EMAIL}</a>
            </p>
            <p style="
                margin:14px 0 0; font-size:1.08rem; font-weight:700;
                letter-spacing:0.08em; color:#0c4a6e;
            ">{APP_NAME}</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Small button to open/close the profile uploader ---
btn_col, _ = st.columns([1, 5])
with btn_col:
    label = "🖼 Change photo" if avatar_b64 else "🖼 Upload profile photo"
    if st.button(label, use_container_width=True, key="toggle_avatar"):
        st.session_state.show_profile_uploader = not st.session_state.show_profile_uploader
        st.rerun()

if st.session_state.show_profile_uploader:
    with st.container(border=True):
        st.markdown("##### Profile picture")
        new_pic = st.file_uploader(
            "Upload a square image (PNG/JPG, under 2 MB is best)",
            type=["png", "jpg", "jpeg", "webp", "gif"],
            key="avatar_upload",
        )
        c1, c2, c3 = st.columns([1, 1, 4])
        with c1:
            if st.button("Save", use_container_width=True, key="avatar_save"):
                if not new_pic:
                    st.warning("Choose a file first.")
                else:
                    save_profile(new_pic)
                    st.session_state.show_profile_uploader = False
                    st.success("Profile picture updated.")
                    st.rerun()
        with c2:
            if avatar_b64 and st.button("Remove", use_container_width=True, key="avatar_remove"):
                delete_profile()
                st.session_state.show_profile_uploader = False
                st.rerun()

st.divider()


# ---------------- Add panels ----------------
tab_upload, tab_url = st.tabs(["➕  Upload HTML app", "🔗  Add URL app (demo)"])

with tab_upload:
    col1, col2, col3 = st.columns([2, 3, 1])
    with col1:
        app_name = st.text_input("App name (optional)", placeholder="My App", key="upload_name")
    with col2:
        uploaded = st.file_uploader(
            "Upload HTML + assets",
            type=["html", "css", "js", "png", "jpg", "jpeg",
                  "svg", "gif", "webp", "json", "txt", "ico"],
            accept_multiple_files=True,
            key="upload_files",
        )
    with col3:
        st.write("")
        st.write("")
        add_clicked = st.button("Upload", use_container_width=True, key="upload_btn")

    if add_clicked:
        if not uploaded:
            st.warning("Pick at least one file first.")
        else:
            folder = safe_name(app_name.strip() or Path(uploaded[0].name).stem)
            target = APPS_DIR / folder
            target.mkdir(parents=True, exist_ok=True)
            for f in uploaded:
                name = Path(f.name).name
                if name:
                    (target / name).write_bytes(f.read())
            st.success(f"Added **{folder}** — refresh to see it below.")
            st.rerun()

    st.caption(
        "Upload `index.html` plus its CSS/JS/images together, "
        "or drop folders straight into `apps/` on GitHub."
    )

with tab_url:
    c1, c2 = st.columns([2, 3])
    with c1:
        url_title = st.text_input("App name", placeholder="My Live Demo", key="url_title")
    with c2:
        url_value = st.text_input("URL", placeholder="https://example.com", key="url_value")

    url_desc = st.text_input(
        "Short description (optional)",
        placeholder="What this demo does…",
        key="url_desc",
    )

    b1, b2 = st.columns([1, 5])
    with b1:
        add_url_clicked = st.button("Add URL", use_container_width=True, key="url_btn")

    if add_url_clicked:
        if not url_title.strip() or not url_value.strip():
            st.warning("Both name and URL are required.")
        elif not re.match(r"^https?://", url_value.strip()):
            st.warning("URL must start with http:// or https://")
        else:
            items = load_url_apps()
            items.append({
                "title": url_title.strip(),
                "url":   url_value.strip(),
                "desc":  url_desc.strip(),
                "key":   safe_name(url_title.strip()),
            })
            save_url_apps(items)
            st.success(f"Added **{url_title}** — refresh to see it below.")
            st.rerun()

    st.caption(
        "⚠️ Some sites (Google, YouTube, Facebook) block embedding. "
        "Your own GitHub Pages / Netlify / Vercel demo links usually work."
    )


# ---------------- App grid ----------------
apps = list_all_apps()

if st.session_state.active_app:
    selected = next((a for a in apps if a["key"] == st.session_state.active_app), None)
    if selected:
        back_col, title_col, open_col = st.columns([1, 4, 1])
        with back_col:
            if st.button("← Back", use_container_width=True):
                st.session_state.active_app = None
                st.rerun()
        with title_col:
            st.subheader(selected["title"])
        with open_col:
            if selected["kind"] == "url":
                st.link_button("Open ↗", selected["url"], use_container_width=True)

        try:
            if selected["kind"] == "url":
                st.iframe(selected["url"], height=900)
            else:
                st.iframe(selected["path"], height=900)
        except Exception as e:
            st.error(f"Could not load app: {e}")
            if selected["kind"] == "url":
                st.markdown(f"[Open in a new tab ↗]({selected['url']})")
    else:
        st.session_state.active_app = None
        st.rerun()

else:
    if not apps:
        st.info(
            "No apps yet. Upload an HTML file, add a URL, "
            "or push a folder into `apps/` on GitHub."
        )
    else:
        st.subheader(f"Your apps ({len(apps)})")
        cols_per_row = 3
        for i in range(0, len(apps), cols_per_row):
            row = apps[i : i + cols_per_row]
            cols = st.columns(cols_per_row)

            for col, a in zip(cols, row):
                with col:
                    with st.container(border=True):
                        st.markdown(f"### 🧩 {a['title']}")

                        if a["kind"] == "url":
                            st.markdown(
                                '<span class="badge badge-url">URL · DEMO</span>',
                                unsafe_allow_html=True,
                            )
                            st.caption(a.get("url", ""))
                        else:
                            st.markdown(
                                '<span class="badge badge-file">LOCAL HTML</span>',
                                unsafe_allow_html=True,
                            )
                            st.caption(f"`{a['key']}`")

                        btn1, btn2 = st.columns([3, 1])
                        with btn1:
                            if st.button(
                                "Open",
                                key=f"open_{a['kind']}_{a['key']}",
                                use_container_width=True,
                            ):
                                st.session_state.active_app = a["key"]
                                st.rerun()
                        with btn2:
                            if st.button(
                                "🗑",
                                key=f"del_{a['kind']}_{a['key']}",
                                use_container_width=True,
                            ):
                                if a["kind"] == "url":
                                    items = [
                                        u for u in load_url_apps()
                                        if safe_name(u.get("title", "")) != a["key"]
                                    ]
                                    save_url_apps(items)
                                else:
                                    target = APPS_DIR / a["key"]
                                    if target.exists():
                                        if target.is_dir():
                                            shutil.rmtree(target)
                                        else:
                                            target.unlink()
                                st.rerun()


# ---------------- Footer ----------------
st.divider()
st.markdown(
    f"""
    <div style="
        text-align:center; padding: 18px;
        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
        border: 1px solid #7dd3fc;
        border-radius: 14px;
        color:#0c4a6e; font-size:0.88rem;
        margin-top: 8px;
    ">
        <strong>{YOUR_NAME}</strong> — {YOUR_TITLE}<br>
        📞 {YOUR_PHONE} &nbsp;·&nbsp;
        ✉️ <a href="mailto:{YOUR_EMAIL}" style="color:#0284c7; text-decoration:none;">{YOUR_EMAIL}</a>
    </div>
    """,
    unsafe_allow_html=True,
)
