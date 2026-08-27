# WorkHub Auth Service

The Auth Service is responsible for authentication and authorization
functionality in the WorkHub application.

It is implemented using FastAPI and follows a layered architecture.

## Responsibilities

The Auth Service handles:

- User login
- JWT access token generation
- Refresh token generation
- Refresh token validation
- Logout
- Change password
- Forgot password
- Password reset
- Password hashing
- Authentication validation

## Architecture

```text
Client
  |
  v
API Route
  |
  v
Auth Service
  |
  +---------> User Client ---------> User Service
  |
  +---------> Token Repository
                  |
                  v
               auth.db