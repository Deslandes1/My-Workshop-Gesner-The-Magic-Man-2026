"""
Nest — My HTML App Hub
Built by: Gesner Deslandes — Software Engineer
Contact: (509)-47385663 · deslandes78@gmail.com
"""

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
# ==============================================

APPS_DIR.mkdir(exist_ok=True)

st.set_page_config(
    page_title=f"{APP_NAME} · {YOUR_NAME}",
    page_icon="🪺",
    layout="wide",
)


# ---------------- Helpers ----------------
def list_apps():
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
                "kind": "folder",
            })
        elif entry.suffix.lower() == ".html":
            apps.append({
                "title": entry.stem.replace("-", " ").replace("_", " ").title(),
                "path": entry,
                "key": entry.name,
                "kind": "file",
            })
    return apps


def safe_name(raw: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_\- ]", "", raw).strip()
    return cleaned.replace(" ", "-") or "app"


# ---------------- Session state ----------------
if "active_app" not in st.session_state:
    st.session_state.active_app = None


# ---------------- Header ----------------
st.markdown(
    f"""
    <div style="text-align:center; padding: 28px 0 12px;">
        <h1 style="
            margin:0; font-size:2.9rem; font-weight:800; letter-spacing:-0.02em;
            background: linear-gradient(90deg,#2563eb,#7c3aed);
            -webkit-background-clip: text; background-clip: text;
            color: transparent;
        ">{YOUR_NAME}</h1>
        <p style="
            margin:8px 0 0; font-size:1rem; font-weight:600;
            letter-spacing:0.14em; color:#475569; text-transform:uppercase;
        ">{YOUR_TITLE}</p>
        <p style="margin:10px 0 0; font-size:0.95rem; color:#64748b;">
            📞 {YOUR_PHONE} &nbsp;·&nbsp; ✉️
            <a href="mailto:{YOUR_EMAIL}" style="color:#2563eb; text-decoration:none;">{YOUR_EMAIL}</a>
        </p>
        <p style="
            margin:18px 0 0; font-size:1.15rem; font-weight:700;
            letter-spacing:0.08em; color:#0f172a;
        ">{APP_NAME}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()


# ---------------- Upload panel ----------------
with st.expander("➕  Add a new app", expanded=False):
    col1, col2, col3 = st.columns([2, 3, 1])
    with col1:
        app_name = st.text_input("App name (optional)", placeholder="My App")
    with col2:
        uploaded = st.file_uploader(
            "Upload HTML + assets",
            type=["html", "css", "js", "png", "jpg", "jpeg",
                  "svg", "gif", "webp", "json", "txt", "ico"],
            accept_multiple_files=True,
        )
    with col3:
        st.write("")
        st.write("")
        add_clicked = st.button("Upload", use_container_width=True)

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
        "Tip: upload `index.html` plus its CSS/JS/images together. "
        "You can also drop folders straight into `apps/` on GitHub."
    )


# ---------------- App grid ----------------
apps = list_apps()

if st.session_state.active_app:
    selected = next((a for a in apps if a["key"] == st.session_state.active_app), None)
    if selected:
        back_col, title_col = st.columns([1, 5])
        with back_col:
            if st.button("← Back", use_container_width=True):
                st.session_state.active_app = None
                st.rerun()
        with title_col:
            st.subheader(selected["title"])
        try:
            st.iframe(selected["path"], height=900)
        except Exception as e:
            st.error(f"Could not load app: {e}")
    else:
        st.session_state.active_app = None
        st.rerun()
else:
    if not apps:
        st.info("No apps yet. Upload an HTML file above, or push a folder into `apps/` on GitHub.")
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
                        st.caption(f"{a['kind']} · `{a['key']}`")
                        btn1, btn2 = st.columns([3, 1])
                        with btn1:
                            if st.button("Open", key=f"open_{a['key']}", use_container_width=True):
                                st.session_state.active_app = a["key"]
                                st.rerun()
                        with btn2:
                            if st.button("🗑", key=f"del_{a['key']}", use_container_width=True):
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
    <div style="text-align:center; padding: 16px 0 8px; color:#94a3b8; font-size:0.85rem;">
        © {YOUR_NAME} — {YOUR_TITLE}<br>
        📞 {YOUR_PHONE} &nbsp;·&nbsp;
        ✉️ <a href="mailto:{YOUR_EMAIL}" style="color:#2563eb; text-decoration:none;">{YOUR_EMAIL}</a>
    </div>
    """,
    unsafe_allow_html=True,
)
