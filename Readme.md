### README

# Light Hat Texts

Light Hat Texts is a Django application that allows users to submit and vote on short text messages (up to 8 characters) to be displayed on a LED-covered hat. Users can upvote or downvote messages, and the application will periodically send the most popular text to the LED hat.

## Features

- Submit new text messages (up to 8 characters)
- Upvote and downvote messages
- Periodically updates to show the latest messages
- Send texts to a worker queue on a periodic schedule, where they are forwarded to the LED hat

## Prerequisites

- Docker
- Docker Compose

## Getting Started

### Build and Run the Application

1. Ensure Docker and Docker Compose are installed on your machine.
2. Run the following command to build and start the containers:

```bash
docker-compose up --build
```

This command will:

- Build the Docker images for the Django application and the database.
- Start the containers defined in the `docker-compose.yml` file.

### Access the Application

Once the containers are up and running, you can access the application at:

```
http://localhost:8000
```

### Stopping the Application

To stop the running containers, press `Ctrl+C` in the terminal where `docker-compose` is running, then execute:

```bash
docker-compose down
```

This command will stop and remove the containers.

## Project Structure

- `Dockerfile`: Defines the Docker image for the Django application.
- `docker-compose.yml`: Defines the services (Django app and database) and how they interact.
- `emf_hat/`: Contains the Django configuration.
- `hat_api/`: Contains the the hat text controller code and the webpage.

## Configuration

- The Django application uses SQLite by default, but you can configure it to use other databases by modifying the `settings.py` file.
- Environment variables can be set in the `docker-compose.yml` file to configure the application.

## License

This project is licensed under the MIT License.
