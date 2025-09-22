import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="PDF Chatbot", page_icon="📄", layout="centered")

st.title("📄 PDF Chatbot")

# --- Initialize session state ---
if "messages" not in st.session_state:
    st.session_state["messages"] = []  # chat history
if "pdf_uploaded" not in st.session_state:
    st.session_state["pdf_uploaded"] = False

# --- File Upload ---
st.header("Upload PDF")

uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    if st.button("Upload PDF"):
        files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
        try:
            response = requests.post(f"{API_BASE}/upload-pdf", files=files)
            data = response.json()

            if response.status_code == 200 and data.get("status") == 200:
                st.success(data.get("message", "PDF uploaded successfully!"))
                st.session_state["pdf_uploaded"] = True
                st.session_state["messages"] = []  # reset chat after new upload
            else:
                error_detail = data.get("results", {}).get("detail", ["Unknown error"])[0]
                error_code = data.get("status", "N/A")
                st.error(f"Error {error_code}: {error_detail}")

        except Exception as e:
            st.error(f"⚠️ Could not connect to API: {e}")

# --- Chat Interface ---
if st.session_state["pdf_uploaded"]:
    st.header("Chat with your PDF")

    # Display previous messages
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input box at the bottom
    if question := st.chat_input("Ask a question about the PDF..."):
        # Add user message
        st.session_state["messages"].append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        # Call API
        try:
            response = requests.post(f"{API_BASE}/ask", json={"question": question})
            data = response.json()

            if response.status_code == 200 and data.get("status") == 200:
                answer = data.get("results", {}).get("answer", "No answer found.")
                st.session_state["messages"].append({"role": "assistant", "content": answer})
                with st.chat_message("assistant"):
                    st.markdown(answer)
            else:
                error_detail = data.get("results", {}).get("detail", ["Unknown error"])[0]
                error_code = data.get("status", "N/A")
                error_msg = f"Error {error_code}: {error_detail}"
                st.session_state["messages"].append({"role": "assistant", "content": error_msg})
                with st.chat_message("assistant"):
                    st.error(error_msg)

        except Exception as e:
            error_msg = f"⚠️ Could not connect to API: {e}"
            st.session_state["messages"].append({"role": "assistant", "content": error_msg})
            with st.chat_message("assistant"):
                st.error(error_msg)
