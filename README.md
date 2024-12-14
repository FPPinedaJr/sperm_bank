# Sperm Bank Management System API

A Flask-based RESTful API for managing a sperm bank's data, including role types, relationship types, donations, and individuals. The application uses MySQL for the database and JWT for authentication and role-based access control.

## Features

- **Authentication**: Register and login functionality with password hashing and JWT-based token authentication.
- **Role-Based Access Control**: APIs with admin-restricted operations.
- **CRUD Operations**: Full CRUD for:
  - Role Types
  - Relationship Types
  - Donations
  - Individuals
  - Relationships
- **Secure Access**: Uses JWT for user authentication.

## Technologies Used

- **Backend**: Flask
- **Database**: MySQL
- **Authentication**: JWT (JSON Web Tokens)
- **Python Libraries**:
  - `flask`
  - `flask_mysqldb`
  - `flask_jwt_extended`
  - `MySQLdb`

## Getting Started

### Prerequisites

- Python 3.9+
- MySQL Server
- pip (Python package manager)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/FPPinedaJr/sperm_bank.git
   cd sperm_bank
   ```

2. Create a virtual environment:

   ```bash
   python -m venv .venv
   .venv/scripts/activate
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure the database:

   - Create a MySQL database named `spermbank`.
   - Update the `app.config` values for `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, and `MYSQL_DB` in `app.py`.

5. Run the application:
   ```bash
   flask run
   ```
   The application will be accessible at `http://localhost:5000`.

## API Documentation

### Authentication Endpoints

| Endpoint             | Method | Description                  | Auth Required | Admin Only |
| -------------------- | ------ | ---------------------------- | ------------- | ---------- |
| `/api/auth/register` | POST   | Register a new user          | No            | No         |
| `/api/auth/login`    | POST   | Authenticate and get a token | No            | No         |

### Role Types

| Endpoint               | Method | Description            | Auth Required | Admin Only |
| ---------------------- | ------ | ---------------------- | ------------- | ---------- |
| `/api/role_types`      | GET    | Get all role types     | Yes           | No         |
| `/api/role_types/{id}` | GET    | Get a role type by ID  | Yes           | No         |
| `/api/role_types`      | POST   | Create a new role type | Yes           | Yes        |
| `/api/role_types/{id}` | PUT    | Update a role type     | Yes           | Yes        |
| `/api/role_types/{id}` | DELETE | Delete a role type     | Yes           | Yes        |

### Relationship Types

| Endpoint                       | Method | Description                    | Auth Required | Admin Only |
| ------------------------------ | ------ | ------------------------------ | ------------- | ---------- |
| `/api/relationship_types`      | GET    | Get all relationship types     | Yes           | No         |
| `/api/relationship_types/{id}` | GET    | Get a relationship type by ID  | Yes           | No         |
| `/api/relationship_types`      | POST   | Create a new relationship type | Yes           | Yes        |
| `/api/relationship_types/{id}` | PUT    | Update a relationship type     | Yes           | Yes        |
| `/api/relationship_types/{id}` | DELETE | Delete a relationship type     | Yes           | Yes        |

### Donations

| Endpoint              | Method | Description           | Auth Required | Admin Only |
| --------------------- | ------ | --------------------- | ------------- | ---------- |
| `/api/donations`      | GET    | Get all donations     | Yes           | No         |
| `/api/donations/{id}` | GET    | Get a donation by ID  | Yes           | No         |
| `/api/donations`      | POST   | Create a new donation | Yes           | Yes        |
| `/api/donations/{id}` | PUT    | Update a donation     | Yes           | Yes        |
| `/api/donations/{id}` | DELETE | Delete a donation     | Yes           | Yes        |

### Individuals

| Endpoint                | Method | Description            | Auth Required | Admin Only |
| ----------------------- | ------ | ---------------------- | ------------- | ---------- |
| `/api/individuals`      | GET    | Get all individuals    | Yes           | No         |
| `/api/individuals/{id}` | GET    | Get a individual by ID | Yes           | No         |
| `/api/individuals`      | POST   | Add a new individual   | Yes           | Yes        |
| `/api/individuals/{id}` | PUT    | Update an individual   | Yes           | Yes        |
| `/api/individuals/{id}` | DELETE | Delete an individual   | Yes           | Yes        |

### Relationships

| Endpoint                  | Method | Description                           | Auth Required | Admin Only |
| ------------------------- | ------ | ------------------------------------- | ------------- | ---------- |
| `/api/relationships`      | GET    | Get all relationships                 | Yes           | No         |
| `/api/relationships/{id}` | GET    | Get a relationship by ID              | Yes           | No         |
| `/api/relationships`      | POST   | Add a new relationship                | Yes           | Yes        |
| `/api/relationships/{id}` | PUT    | Update an existing relationship by ID | Yes           | Yes        |
| `/api/relationships/{id}` | DELETE | Delete an existing relationship by ID | Yes           | Yes        |

### Notes:

1. **Auth Required**: Indicates whether a JWT token is required in the `Authorization` header.
2. **Admin Only**: Some endpoints are restricted to users with admin privileges.
3. `{id}`: Replace `{id}` in the endpoint with the actual ID of the resource you want to manipulate.
