# Django REST API E-commerce Project

This project is a simple e-commerce API built with Django and Django REST Framework. It includes authentication and authorization using token-based authentication with `rest_framework.authtoken`.

## Features

- User registration and authentication
    - Use the registration endpoint to create a new user.
    - Use the login endpoint to obtain a token.
    - Include the token in the Authorization header to access protected endpoints.
- Token-based authentication and authorization
- Product listing, creation, update, and deletion
- Basic order management
  

## Getting Started

These instructions will help you set up and run the project on your local machine for development and testing purposes.

### Prerequisites

- Python 3.x
- Django
- Django REST Framework
- `rest_framework.authtoken` (for token authentication)

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/bedinir/django-rest-api.git
   cd django-rest-api
