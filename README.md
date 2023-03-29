# Injozi Backend

## Requirements

Create a Python REST API utilising Flask with the following capabilities

1. Data should be stored in MONGODB
2. JWT Authentication
3. CRUD Operations (Create, Read, Update, Delete).
4. Please follow The OpenAPI Specification (OAS).

Routes:

- [x] Register
- [x] Login
- [ ] Profile (Protected Route)
- [ ] List Profiles

Bonus:

- [ ] Code comments
- [ ] Error Handling
- [ ] Audit Logs

## Additional

We would like for you to build your application to run on a docker container port 5003:5003.

- We should be able to run compose up to build and test the application
- The application needs to build itself with all the needed requirements installed.

Bonus points (Not a must)

- [ ] A simple design of the architecture
- [x] Secure encryption on passwords
- [x] Connecting the DB on https://www.mongodb.com/
- [ ] Using a config file for importing passwords and settings that will help the application run
- [ ] Simple Unit tests
- [ ] Test cases

## Commands

### Run

```
flask --app hello run --debug
```

### Virtual Environment

```
python -m venv venv
```

```
.\venv\Scripts\Activate.ps1
```
