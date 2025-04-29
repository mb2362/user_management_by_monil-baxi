# Project Setup and Configuration

This project includes a comprehensive setup involving multiple services such as MinIO for object storage and PostgreSQL for data management. The Docker-based configuration ensures that all services communicate seamlessly, with explicit network bindings and persistent storage volumes.

## Issues Addressed

1. **Container Names:**
   - Explicit `container_name` settings were added to all services to ensure predictable service names for service discovery, logging, and debugging.

2. **MinIO Service:**
   - A MinIO service was added for object storage with ports 9000 (MinIO server) and 9001 (console).
   - Environment variables for MinIO root credentials were set, and a volume was added for persistent storage.

3. **Volume Mounts:**
   - Persistent storage volumes were defined for MinIO data storage (`minio_data`), alongside existing volumes for PostgreSQL (`postgres-data`) and pgAdmin (`pgadmin-data`).

4. **PostgreSQL User:**
   - The PostgreSQL user configuration was standardized across the project. A custom user (`user1`) was defined to ensure clarity and consistency.

5. **Network Configuration:**
   - Explicit network configurations were added to ensure all services are correctly isolated and can communicate with each other within the same network.

## Prerequisites

Before you begin, ensure you have the following installed:
- Docker
- Docker Compose

## Configuration

### Docker Compose File

Ensure that your `docker-compose.yml` includes the following configurations:

```yaml
version: "3.7"

services:
  # MinIO Service for Object Storage
  minio:
    container_name: minio-service
    image: minio/minio
    environment:
      - MINIO_ROOT_USER=your-access-key
      - MINIO_ROOT_PASSWORD=your-secret-key
    volumes:
      - minio_data:/data
    ports:
      - "9000:9000"
      - "9001:9001"
    networks:
      - app-network

  # PostgreSQL Service
  postgres:
    container_name: postgres-db
    image: postgres:13
    environment:
      - POSTGRES_USER=user1
      - POSTGRES_PASSWORD=your-password
      - POSTGRES_DB=your-db
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - app-network

  # pgAdmin Service
  pgadmin:
    container_name: pgadmin
    image: dpage/pgadmin4
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@admin.com
      - PGADMIN_DEFAULT_PASSWORD=your-password
    ports:
      - "5050:80"
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  minio_data:
  postgres-data:
  pgadmin-data:
```

## Network Configuration
We define a custom network app-network to ensure that all services can communicate with each other securely. This ensures that the services are isolated and do not interfere with other containers running on the system.

## MinIO Service
The MinIO service is configured with root credentials and persistent storage. MinIO can be accessed via the following ports:

MinIO Server: http://localhost:9000

MinIO Console: http://localhost:9001

PostgreSQL and pgAdmin
The PostgreSQL service uses a custom user user1 for database access. pgAdmin is set up for easy management of PostgreSQL via a web interface, accessible at:

pgAdmin: http://localhost:5050

Running the Application
To get the project up and running, use the following steps:

## Clone the repository to your local machine:

```sh
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```

## Build and start the services:

```sh
docker compose up -d
```
## Access the services:

MinIO Console: http://localhost:9001

pgAdmin: http://localhost:5050

PostgreSQL: your-db (configured in docker-compose.yml)

To stop the services:

```sh
docker compose down -v
```

## Conclusion
This configuration ensures proper networking, persistent storage, and clear service definitions for better predictability and reliability. Each service is isolated within its own network, and volume mounts are defined to retain data even after containers are restarted.