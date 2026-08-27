# WorkHub User Service

The User Service is responsible for user management and user data.

It owns the User model and User database.

## Responsibilities

The User Service handles:

- User registration
- User information
- User lookup
- User management
- User database operations
- Internal APIs used by other services

## Architecture

```text
Client / Other Services
          |
          v
      API Routes
          |
          v
    User Service
          |
          v
   User Repository
          |
          v
      User Model
          |
          v
       user.db