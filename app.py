# app.py
import streamlit as st
import requests
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE = os.getenv("BASE_API")

st.set_page_config(page_title="PDF Chatbot (UI)", page_icon="🤖", layout="wide")

# ---------- Styling ----------
st.markdown(
    """
    <style>
    /* page */
    .appview-container .main .block-container{
        padding-top: 1rem;
        padding-right: 2rem;
        padding-left: 2rem;
    }

    /* chat bubble base */
    .chat-bubble {
        padding: 12px 14px;
        border-radius: 14px;
        display: inline-block;
        max-width: 100%;
        line-height: 1.4;
        font-size: 14px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        white-space: pre-wrap;
        word-wrap: break-word;
    }

    /* bot (left) */
    .bot {
        background: linear-gradient(180deg, #ffffff 0%, #f3f4f6 100%);
        color: #111827;
        border: 1px solid rgba(2,6,23,0.05);
        border-top-left-radius: 6px;
    }

    /* user (right) */
    .user {
        background: linear-gradient(180deg, #e6f7ff 0%, #dff6ff 100%);
        color: #0f172a;
        border: 1px solid rgba(14,165,233,0.12);
        border-top-right-radius: 6px;
    }

    /* small avatar circle */
    .avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: inline-block;
        text-align: center;
        line-height: 36px;
        font-weight: 600;
        margin-right: 8px;
        font-size: 14px;
    }
    .bot-avatar { background: #0ea5a4; color: white; }
    .user-avatar { background: #0284c7; color: white; }

    /* align helper */
    .left-col { display: flex; align-items: flex-start; gap: 8px; margin: 10px 0 16px 0; }
    .right-col { display: flex; justify-content: flex-end; align-items: flex-start; gap: 8px; margin: 10px 0 16px 0; }

    /* smaller metadata text */
    .meta { font-size: 12px; color: #6b7280; margin-top: 6px; }

    /* file info box */
    .file-box {
        padding: 10px;
        border-radius: 8px;
        background: #f8fafc;
        border: 1px dashed rgba(15,23,42,0.06);
        font-size: 13px;
    }

    /* add breathing room above chat input */
    [data-testid="stChatInput"] { margin-top: 18px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Session state ----------
if "messages" not in st.session_state:
    st.session_state["messages"]: List[Dict] = []  # each item: {"role": "user"/"assistant", "content": "..."}
if "pdf_uploaded" not in st.session_state:
    st.session_state["pdf_uploaded"] = False
if "pdf_name" not in st.session_state:
    st.session_state["pdf_name"] = None
if "pdf_status" not in st.session_state:
    st.session_state["pdf_status"] = None

# ---------- Layout ----------
left_col, main_col, right_col = st.columns([1, 6, 1])
with left_col:
    st.write("")  # spacer
with main_col:
    st.title("📄 PDF Chatbot — Streamlit UI")
    st.write("Upload a PDF, then chat with the document. Bot replies appear on the left; your messages are on the right.")

with right_col:
    st.write("")

# ---------- Sidebar: Upload / Info ----------
with st.sidebar:
    st.header("Document")
    uploaded_file = st.file_uploader("Upload PDF (only PDF)", type=["pdf"])

    if uploaded_file is not None:
        if st.button("Upload PDF"):
            # send file to backend
            files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
            try:
                resp = requests.post(f"{API_BASE}/upload-pdf", files=files, timeout=30)
                data = resp.json()
            except Exception as e:
                st.error(f"Could not reach backend: {e}")
                data = None
                resp = None

            if resp is None:
                st.session_state["pdf_uploaded"] = False
                st.session_state["pdf_name"] = None
                st.session_state["pdf_status"] = None
            else:
                status_code = data.get("status", resp.status_code) if isinstance(data, dict) else resp.status_code
                if resp.status_code == 200 and status_code == 200:
                    st.success(data.get("message", "PDF processed successfully."))
                    st.session_state["pdf_uploaded"] = True
                    st.session_state["pdf_name"] = uploaded_file.name
                    st.session_state["pdf_status"] = data.get("results", {}).get("status", "processed")
                    # reset chat for fresh doc
                    st.session_state["messages"] = []
                else:
                    # extract details robustly
                    details = []
                    if isinstance(data, dict):
                        results = data.get("results", {})
                        # the API returns results.detail as a list per your example
                        d = results.get("detail")
                        if isinstance(d, list):
                            details = d
                        elif isinstance(d, str):
                            details = [d]
                        else:
                            details = ["Unknown error"]
                    else:
                        details = ["Unknown error"]

                    # show pop-up style error in sidebar and add to chat as assistant message
                    err_text = f"Error {status_code}: {details[0]}"
                    st.error(err_text)
                    st.session_state["pdf_uploaded"] = False
                    st.session_state["pdf_name"] = uploaded_file.name
                    st.session_state["pdf_status"] = f"error ({status_code})"
                    # also append to chat history as assistant error bubble
                    st.session_state["messages"].append({"role": "assistant", "content": err_text})

    # show file info
    if st.session_state["pdf_name"]:
        st.markdown(
            f"<div class='file-box'><strong>File:</strong> {st.session_state['pdf_name']}<br>"
            f"<strong>Status:</strong> {st.session_state.get('pdf_status', 'N/A')}</div>",
            unsafe_allow_html=True,
        )
    else:
        st.info("No PDF uploaded yet.")

    st.markdown("---")
    st.markdown(f"Run backend at {API_BASE}")
    st.markdown("Run frontend with:\n```\nstreamlit run app.py --server.port 8001\n```")

# ---------- Helper: render message ----------
def render_message(msg: Dict):
    role = msg.get("role")
    text = msg.get("content", "")
    if role == "assistant":
        cols = st.columns([0.8, 0.2])
        with cols[0]:
            # left column: avatar + bubble
            avatar_html = "<div class='avatar bot-avatar'>B</div>"
            bubble_html = f"<div class='chat-bubble bot'>{text}</div>"
            st.markdown(f"<div class='left-col'>{avatar_html}{bubble_html}</div>", unsafe_allow_html=True)
        # right empty
        with cols[1]:
            st.write("")
    else:  # user
        cols = st.columns([0.2, 0.8])
        with cols[0]:
            st.write("")
        with cols[1]:
            avatar_html = "<div class='avatar user-avatar'>You</div>"
            bubble_html = f"<div class='chat-bubble user'>{text}</div>"
            st.markdown(f"<div class='right-col'>{bubble_html}{avatar_html}</div>", unsafe_allow_html=True)

# ---------- Main Chat area ----------
chat_container = st.container()
with chat_container:
    st.header("Chat")
    # Display chat history
    for m in st.session_state["messages"]:
        render_message(m)

    if not st.session_state["pdf_uploaded"]:
        st.info("Please upload and process a PDF first (use the sidebar).")
    else:
        # chat input
        question = st.chat_input("Ask something about the document...")
        if question:
            # append user's message
            st.session_state["messages"].append({"role": "user", "content": question})

            # call backend /ask
            try:
                resp = requests.post(f"{API_BASE}/ask", json={"question": question}, timeout=30)
                data = resp.json()
            except Exception as e:
                err = f"Could not contact backend: {e}"
                st.session_state["messages"].append({"role": "assistant", "content": err})
            else:
                status_code = data.get("status", resp.status_code) if isinstance(data, dict) else resp.status_code
                if resp.status_code == 200 and status_code == 200:
                    answer = data.get("results", {}).get("answer", "No answer.")
                    st.session_state["messages"].append({"role": "assistant", "content": answer})
                else:
                    # get detail message
                    results = data.get("results", {}) if isinstance(data, dict) else {}
                    detail = results.get("detail", ["Unknown error"]) 
                    if isinstance(detail, list):
                        detail_text = detail[0]
                    else:
                        detail_text = str(detail)
                    err_text = f"Error {status_code}: {detail_text}"
                    st.session_state["messages"].append({"role": "assistant", "content": err_text})

            # re-render so chat history appears above the input consistently
            st.rerun()

# ---------- Footer controls ----------
st.markdown("---")
cols = st.columns([1, 1])
with cols[0]:
    if st.button("🧹 Clear chat", use_container_width=True, help="Remove all chat messages"):
        st.session_state["messages"] = []
        st.toast("Chat cleared")
with cols[1]:
    if st.button("♻️ Reset uploaded PDF", type="primary", use_container_width=True, help="Clear the current PDF and chat state"):
        st.session_state["pdf_uploaded"] = False
        st.session_state["pdf_name"] = None
        st.session_state["pdf_status"] = None
        st.session_state["messages"] = []
        st.toast("PDF state reset")
