
```markdown
# Event Management API

This is a FastAPI-based Event Management API that allows users to manage events, register attendees, check-in attendees, and handle event statuses. The API uses PostgreSQL as the database and follows REST API principles.

## Features

- **Event Management**:
  - Create, update, and delete events.
  - List events with filters.
  - Auto-complete past events.
  
- **Attendee Registration**:
  - Register attendees with limits.
  - Check-in attendees via a CSV upload.

- **Status Management**:
  - Automatic status updates for attendees.

---
```
## Project Structure

```
.
├── .env
├── README.md
├── requirements.txt
├── main.py
├── common
│   ├── __init__.py
│   ├── config.py
│   ├── db.py
│   ├── middleware.py
│   └── response.py
├── event
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── schemas.py
│   └── views.py

```

- **`common/`**: Contains shared modules like database configuration, middleware, and custom response models.
- **`event/`**: Contains models, schemas, views, and routing related to event and registration logic.
- **`main.py`**: Entry point of the application where the FastAPI app is initialized and routers are included.
- **`.env`**: Environment variables for configuration.
- **`requirements.txt`**: Python dependencies for the project.
- **`README.md`**: Project documentation.

---
## Prerequisites

Ensure you have the following installed:

- Python 3.8+
- PostgreSQL

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/J-Bhuvanesh/EventManagement.git
    cd EventManagement
    git checkout development
    ```

2. Create and activate a virtual environment (optional but recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Set up environment variables in `.env`:

    ```
    DATABASE_URL=postgresql://username:password@localhost/dbname
    ```

5. Run the application:

    ```bash
    python main.py
    ```

6. The API will be accessible at `http://localhost:8000`.

---

## API Endpoints

### Event Endpoints

- **POST** `/events/`: Create a new event.
  
- **GET** `/events/`: List events with optional filters (e.g., status, date).
  
- **PUT** `/events/{event_id}/`: Update an existing event.

### Attendee Registration Endpoints

- **POST** `/events/{event_id}/register/`: Register an attendee for an event.

- **POST** `/events/{event_id}/checkin/`: Check in attendees via a CSV file.

---

## CSV Format for Check-in

The CSV file should be in the following format:

```csv
attendee_name,email
John Doe,john.doe@example.com
Jane Smith,jane.smith@example.com

```

----------

## Database Schema

The application uses PostgreSQL and has the following tables:

-   **`events`**: Stores event details.
    
-   **`users`**: Stores user information (attendees).
    
-   **`registrations`**: Stores event registrations, linking users to events.
    
