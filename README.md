# PWP SPRING 2025

# Hour Logger API

## Dependencies

- Python 3+
- SQLAlchemy
- SQLite 3
- Flask

## Dependency installation

To install the necessary depencies, run:

```pip install flask sqlalchemy```

Alternatively, if using requirements.txt file:

```pip install -r requirements.txt```

## Database

- Database Used: SQLite3
- Version: Default version included with Python 3.x

## Setup Instructions

### **1. Clone the Repository**
```
git clone https://github.com/your-repo/hour-logger-api.git
cd hour-logger-api
```
### **2. Create a Virtual Environment**
```
python -m venv .venv
```
On Windows:
```
.venv\Scripts\activate
```
On macOS/Linux:
```
source .venv/bin/activate
```
### **3. Install Dependencies**
```
pip install -r requirements.txt
```
### **4. Generate and Populate the Database**
```
python create_db.py
```
## Verifying Database Creation
After runnin create_db.py, verify the databse with:
```
sqlite3 test.db
```
List the tables to ensure they have been created:
```
.tables
```
## Project Structure
```
📁 hour-logger-api/
├── 📁 src/
│   └── models.py       # ORM models and database population function
├── create_db.py        # Script to create and populate the database
├── test.db             # Populated SQLite database file
├── requirements.txt    # Python dependencies
└── README.md           # Setup instructions
```
# Group information

- Student 1. Matias Leiber mleiber21@student.oulu.fi
- Student 2. Tuukka Rauhala tuukka.rauhala@student.oulu.fi
- Student 3. Roope Karjalainen rkarjala@student.oulu.fi

**Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint, instructions on how to setup and run the client, instructions on how to setup and run the axiliary service and instructions on how to deploy the api in a production environment**
