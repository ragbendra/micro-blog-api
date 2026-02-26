# Micro Blog API

A sleek, fast backend API for a minimal blogging platform. Built with **FastAPI**, **SQLAlchemy**, and **Pydantic**, this application allows users to create accounts, write posts, and interact with a modern backend system.

## 🏗️ How it Works

The Micro Blog API handles data efficiently by splitting operations into specific roles:

*   **`db/database.py`**: Manages the SQLAlchemy connection engine and the `SessionLocal` factory to connect to the SQLite database (`test.db`).
*   **`db/models.py` (The Storage Layer)**: Defines the physical SQLite database tables (`User` and `Post`) and their relationships using SQLAlchemy ORM.
*   **`db/schemas.py` (The API Layer)**: Defines the strict Pydantic data validation models for incoming API requests (e.g., `UserCreate`) and outgoing responses (e.g., `User`). 
*   **`db/crud.py` (The Logic Layer)**: Contains reusable Python functions for performing Create, Read, Update, and Delete operations on the database, acting as the bridge between `models.py` and `schemas.py`.
*   **`main.py` (The Router)**: The FastAPI application entry point. It contains the route definitions, parses incoming HTTP requests, manages database sessions (via dependencies), calls the appropriate `crud.py` functions, and returns the responses.

## 🚀 Getting Started

### Prerequisites

Ensure you have Python 3.8+ installed. The required packages are listed in `requirements.txt`.

### Installation

1.  Clone this repository.
2.  Navigate to the project directory:
    ```bash
    cd micro-blog-api
    ```
3.  (Optional but recommended) Create and activate a virtual environment.
4.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

To start the local development server with auto-reload enabled, run the following command in your terminal:

```bash
uvicorn main:app --reload
```

## 📖 API Documentation

Once the server is running, FastAPI automatically generates interactive documentation. Open your browser and navigate to:

👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

From there, you can view all available endpoints (`/users/`, `/posts/`, etc.), understand the required request body structures, and execute live queries directly against your local database.
