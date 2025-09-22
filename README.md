# 100x-LLM-week2-pdf-chatbot-frontend

Streamlit frontend for **100x-LLM-week2-pdf-chatbot**.\
This app provides an interactive chat UI to upload PDFs, process them
via the FastAPI backend, and ask natural language questions about the
document.

------------------------------------------------------------------------

## 🚀 Features

-   Upload PDF files and send them to the backend for processing\
-   Error handling for non-PDF uploads (displays status + detail)\
-   Chat-style interface for asking questions about the uploaded
    document\
-   Answers retrieved from backend API in real time

------------------------------------------------------------------------

## 📦 Installation

Clone the repository:

``` bash
git clone https://github.com/your-username/100x-LLM-week2-pdf-chatbot-frontend.git
cd 100x-LLM-week2-pdf-chatbot-frontend
```

Create a virtual environment and activate it:

``` bash
python -m venv venv
source venv/bin/activate   # On Linux / macOS
venv\Scripts\activate      # On Windows
```

Install dependencies:

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

## ▶️ Running the App

Make sure your **backend** (FastAPI) is running at
`http://127.0.0.1:8000`.

Start the Streamlit app on **port 8001**:

``` bash
streamlit run app.py --server.port 8001
```

Now open <http://127.0.0.1:8001> in your browser.

------------------------------------------------------------------------

## 📂 Project Structure

    .
    ├── app.py                # Main Streamlit app
    ├── requirements.txt      # Python dependencies
    └── README.md             # Documentation

------------------------------------------------------------------------

## 🛠 API Endpoints Used

-   **Upload PDF**

        POST /upload-pdf
        Content-Type: multipart/form-data

-   **Ask Question**

        POST /ask
        Content-Type: application/json

Both endpoints return: - `message` → success/error message\
- `status` → HTTP status code\
- `results` → either `answer` or `detail` (error info)

------------------------------------------------------------------------

## 📸 Screenshots (optional)

*Add screenshots of PDF upload and chat interface here*

------------------------------------------------------------------------

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you'd like to change.

------------------------------------------------------------------------

## 📄 License

This project is licensed under the MIT License.
