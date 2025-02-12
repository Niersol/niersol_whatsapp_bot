# WhatsApp Assistants Application

This is a Django-based application that allows users to create and manage multiple assistants using the WhatsApp Business API. Each assistant is configured with a unique phone number ID and assistant ID. The application uses the Assistant API for handling assistant operations.

## Features

- Create and manage multiple assistants for WhatsApp Business accounts.
- Simple configuration by adding phone number IDs and assistant IDs for each assistant.
- Scalable deployment using Docker and Docker Compose.

## Prerequisites

- Docker installed on your system.
- WhatsApp Business API credentials, including phone number ID and assistant ID for each assistant.

## Environment Variables

The application requires environment variables for configuration. Ensure you have set the necessary environment variables before running the application.

## Installation and Setup

1. Clone this repository:
   ```bash
   git clone <repository_url>
   cd <repository_folder>
   ```

2. Build and run the application using Docker Compose:
   ```bash
   docker compose -f docker-compose.prod.yml up -d --build
   ```

3. Access the application at the provided URL after the container is running.

## Configuration

To set up an assistant, provide the following details in admin:

- **Phone Number ID**: The ID of the WhatsApp Business phone number.
- **Assistant ID**: The unique identifier for the assistant.

These values can be added directly in the application interface or via the environment variables.

## Usage

Once the application is running, you can:

- Add phone number IDs and assistant IDs for each assistant.
- Manage multiple assistants for different business phone numbers.

## Deployment

This application is designed for production deployment using Docker. Ensure Docker is properly configured on your server.

## License

This project is licensed under the MIT License.
