# DataApp

DataApp is a full-stack web application built with Flask that allows users to register, upload CSV files, and visualize their data dynamically using Google Charts. It provides a RESTful API for data retrieval, filtering, updating, and deletion. The user interface is built with Bootstrap 5 to create a modern, responsive dashboard featuring both a top navbar (with KPIs) and a side navbar for navigation.

## Features

- **User Authentication:** Secure registration, login, and logout.
- **CSV Upload:** Users can upload CSV files, which are stored in a SQLite database.
- **Dashboard:** View uploaded datasets with options to view, filter, and delete each dataset.
- **Interactive Visualizations:** Generate dynamic charts (pie, bar, line, etc.) using Google Charts with interactive filtering and zooming.
- **RESTful API:** Endpoints for data retrieval, filtering, updating, and deletion.
- **Responsive Design:** Modern UI using Bootstrap 5, featuring a top navbar with KPIs and a side navbar for navigation.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/AbikGrg/Data-Programming-Final.git
   cd Data-Programming-Final

2. **Create a virtual environment:**
   python -m venv .venv
   
3. **Activate the Virtual Environment:**
  On **Windows**:
   ```bash
   .\.venv\Scripts\activate


On **macOS/Linux**: source .venv/bin/activate

5. **Install Dependencies:**
   pip install Flask Flask-SQLAlchemy

6. **Run the Application:**
  python app.py
 
