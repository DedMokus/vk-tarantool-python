# Tarantool KV-storage API

simple api service offering to write and read data in batches from kv-storage based on tarantool.

## Technologies

- **Python**
- **Tarantool**
- **Docker & Docker Compose**
- **JWT for Authentication**

## Getting Started

Here's how to get the project up and running on your local machine for development and testing.

### Prerequisites

- Docker
- Docker Compose

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/DedMokus/vk-tarantool-python.git
   cd vk-tarantool-python
   ```

2. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```
   This spins up the following services:
   - `tarantool-storage`: A Tarantool-based database service.
   - `app`: The main API service application.

### Usage

The marketplace service is accessible at `http://localhost:8000` after startup.

#### Endpoints Overview

- **POST `/login`**: Authenticate existing users.
- **POST `/register`**: Register new users.
- **POST `/read`**: Read values by keys (JWT authentication required).
- **POST `/write`**: Write key-value pairs to database(JWT authentication required).

## Example Commands & Test Data

### Register a User

```bash
curl -X POST http://localhost:8000/register \
     -H "Content-Type: application/json" \
     -d '{"username":"testuser", "password":"password"}'
```
**Response:**
```json
{"status": "success", "username": "testuser"}
```

### User Login

```bash
curl -X POST http://localhost:8000/login \
     -H "Content-Type: application/json" \
     -d '{"username":"testuser", "password":"password"}'
```
**Response:**
```json
{
  "token": "<JWT_TOKEN>",
}
```

### Write data

```bash
curl -X GET "http://localhost:8080/\
            -H 'accept: application/json' \
            -H 'Authorization: Bearer <JWT_TOKEN>' \
            -H 'Content-Type: application/json' \
            -d '{
                "data": {
                    "additionalProp1": "string",
                    "additionalProp2": "string",
                    "additionalProp3": "string"
                }
            }' 
```
**Sample Response:**
```json
{
  "status": "success"
}
```

### Read data

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/app/read' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <JWT_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{
  "keys": [
    "additionalProp1",
    "additionalProp2"
  ]
}'
```
**Response:**
```json
{
  "data": {
    "additionalProp1": "string",
    "additionalProp2": "string"
  }
}
```

### Environment Configuration

The service uses these environment variables, as specified in the Docker Compose file:
- Database connection: `DB_USER_NAME`, `DB_USER_PASSWORD`
- JWT secrets for token management: `SECRET_KEY`, `ALGORITHM`

### Error codes

This API provides following error codes:
- 3: This data already exists
- 403: Incorrect username or password
- 405: User already exists
- 422: Data format error

### Tests

```bash
    docker-compose exec app pytest
```
