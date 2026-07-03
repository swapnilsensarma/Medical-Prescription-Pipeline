# 💊 Medical Prescription Pipeline API

An end-to-end image processing and machine learning backend pipeline that extracts text from medical prescriptions using optical character recognition (OCR) and cross-references it with a MySQL database of valid medicines using fuzzy string matching.

## 🚀 Features
* **OCR Extraction:** Uses EasyOCR to read raw text from uploaded prescription images.
* **Intelligent Matching:** Utilizes RapidFuzz to intelligently match extracted text against a massive database, filtering out noise, artifacts, and irrelevant dosage instructions.
* **FastAPI Architecture:** Provides a high-performance RESTful API with CORS middleware configured for seamless frontend integration.

## 🛠️ Prerequisites
* **Python 3.8+**
* **MySQL Server** (Running locally)

## ⚙️ Local Setup Instructions

### 1. Virtual Environment Setup
* Open your terminal and create a virtual environment:
  `python -m venv .venv`
* Activate the virtual environment:
  `.venv\Scripts\activate`

### 2. Database Configuration
* Open your MySQL Command Line or Workbench.
* Create a new database named `medicines`:
  `CREATE DATABASE medicines;`
* Ensure your local MySQL credentials match the backend configuration (Default: User `root`, Password `password`).
* Run the data-seeding scripts to populate your local database:
  `python import_data.py`
  `python add_prices.py`

### 3. Install Dependencies
* Ensure your terminal is in the project directory.
* Install the required Python packages:
  `pip install -r requirements.txt`

### 4. Run the Server
* Start the FastAPI server using Uvicorn:
  `uvicorn main:app --reload`
* *(Wait for the terminal to print "System Ready..." before sending requests.)*

### 5. Testing the API
* Open your browser and navigate to: `http://127.0.0.1:8000/docs`
* Use the provided Swagger UI to upload a test prescription image (e.g., `test_zip.jpg` or `prescription.jpg`) and execute the endpoint to view the extraction response.
