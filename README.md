
# CodeGPT Assistant

## Table of Contents

- [General Information](#general-information)
- [Description](#description)
- [Technologies](#technologies)
- [Setup](#setup)
  - [Clone the Repository](#clone-the-repository)
  - [Backend Setup (Optional)](#backend-setup)
  - [Environment Setup](#environment-setup)
  - [Database Setup](#database-setup)
  - [Docker Setup](#docker-setup)
  - [Node.js Setup](#nodejs-setup)
- [Running](#running)
  - [Backend Running (Optional)](#backend-running)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Code Quality Analysis](#code-quality-analysis)
- [Status](#status)
- [Created By](#created-by)

## General Information

The CodeGPT Assistant is a Visual Studio Code extension that integrates LangChain and ChatGPT to provide personalized coding assistance. It is specifically optimized for Laravel projects, enabling developers to send code snippets and tasks to an AI model, retrieve context-aware responses, and store interactions in a MongoDB database for future reference.

## Description

CodeGPT Assistant enhances Laravel developers' productivity by embedding AI-powered support within VSCode. The assistant interprets Laravel-specific tasks, generates code snippets, and provides solutions tailored to the Laravel framework. Every interaction is stored, making previous prompts and responses easily accessible.

## Technologies

- **Frontend**:
  - Visual Studio Code Extension (TypeScript)
- **Backend**:
  - Python
  - FastAPI
  - LangChain (for LLM interactions)
  - OpenAI GPT-4 models
- **Database**:
  - MongoDB
- **Others**:
  - Node.js (for extension development)
  - Docker
  - Redis

## Setup

### Clone the Repository

Clone the project repository:

```bash
git clone https://github.com/yourusername/CodeGPT-Assistant.git
```

### Backend Setup (Optional)

Note: The following steps are only necessary if you want to run the backend application without Docker.

Navigate to the backend directory and install Python dependencies:

```bash
cd CodeGPT-Assistant/backend
pip install -r requirements-vm.txt
```

This is important! Creating and activating a virtual environment is required before installing dependencies!

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### Environment Setup

Create a `.env` file in the backend directory with the following variables:

```plaintext
OPENAI_API_KEY=your-openai-api-key
MONGODB_URI=mongodb://mongodb:27017/codegpt
```

or without Docker: 

```plaintext
OPENAI_API_KEY=your-openai-api-key
MONGODB_URI=mongodb://localhost:27017/codegpt
```

Replace placeholders with your actual OpenAI API key.

### Database Setup

Ensure MongoDB is running locally or in the cloud (e.g., MongoDB Atlas). No additional setup is required as collections are dynamically created.

### Docker Setup

Build and start the Docker containers in dev:

```bash
docker-compose --profile dev up
```

Build and start the Docker containers in prod:

```bash
docker-compose --profile prod up
```

This will set up the backend server and MongoDB in Docker containers.

### Node.js Setup

Navigate to the VSCode extension directory and install dependencies:

```bash
cd ../extension
npm install
```

## Running

### Backend Running (optional virtual server)

Note: If the Docker containers are running, the backend is already accessible. 
The following steps are only necessary if you want to run the backend application without Docker.

Start the FastAPI server!

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

### VSCode Extension Running

Open the extension directory in VSCode:

```bash
code extension
```

Press `F5` to launch the extension in a new Extension Development Host window.

## API Endpoints

### 1. `POST /submit`

- **Description**: Processes user prompts and code snippets to provide context-aware responses.
- **Request Body**:
  - `prompt`: Required. The user's question or task.
  - `code`: Optional. Code snippet from the user.
  - `language`: Optional. Specifies the programming language.
- **Example**:
  ```bash
  curl -X POST http://127.0.0.1:8000/submit     -H "Content-Type: application/json"     -d '{"prompt": "How do I create a new migration in Laravel?", "code": "", "language": "PHP"}'
  ```

- **Response**:
  ```json
  {
    "response": "To create a new migration in Laravel, you can use the Artisan command: php artisan make:migration create_users_table..."
  }
  ```

### 2. `GET /history`

- **Description**: Retrieves previous interactions.
- **Query Parameters**:
  - `user_id`: Optional. Filter interactions by user ID if multi-user support is enabled.
- **Example**:
  ```bash
  curl http://127.0.0.1:8000/history?user_id=123
  ```

- **Response**:
  ```json
  [
    {
      "prompt": "How do I create a new migration in Laravel?",
      "response": "To create a new migration in Laravel, you can use the Artisan command..."
    },
    {
      "prompt": "Explain Eloquent relationships.",
      "response": "In Laravel's Eloquent ORM, relationships are defined..."
    }
  ]
  ```

## Testing

### Backend Testing

Run backend tests inside the Docker container:

```bash
docker exec -it codegpt-assistant_backend_1 pytest tests/
```

or without Docker:

```bash
pytest tests/
```

### VSCode Extension Testing

In the extension directory, run:

```bash
npm run test
```

## Code Quality Analysis

### Backend

Run `flake8` and `pylint` for Python code analysis:

```bash
flake8 .
pylint *.py
```

### Extension

Run ESLint for the extension:

```bash
npm run lint
```

## Status

Active

## Created By

Szaniszló Ivor, 2024
