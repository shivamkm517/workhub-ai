# WorkHub AI

WorkHub AI is a backend application built using a microservices architecture.
The project is designed to provide independent services for authentication,
user management, and other features that can be added in the future.

## Architecture

The project currently contains the following services:

```text
                    Frontend
                       |
                       v
                API Gateway
                  (Future)
                       |
              +--------+--------+
              |                 |
              v                 v
        Auth Service       User Service
          :8001               :8002
              |                 |
              v                 v
           auth.db            user.db