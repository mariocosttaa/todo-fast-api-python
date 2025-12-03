# Authentication Flow

## Overview

The application uses a **hybrid authentication model**:

- **JWT access tokens** for cryptographic verification of the user identity.
- A **`sessions` database table** for server-side session tracking, revocation, and expiration.

A request is only considered authenticated if **both** are valid:

1. The JWT is valid (signature + expiry + type).
2. There is a matching, non-expired session row in the `sessions` table.

---

## Components

### Models

- `app/models/user.py`
  - Stores user credentials and profile information (email, hashed password, etc.).

- `app/models/session.py`
  - Table: `sessions`
  - Columns:
    - `id`: UUID (primary key)
    - `user_id`: UUID (FK to `users.id`)
    - `token`: the access token string (JWT)
    - `created_at`: when the session was created
    - `updated_at`: updated on change
    - `last_used_at`: last time this session was used

### Database access

- `app/database/base.py`
  - `get_db()` – FastAPI dependency that yields a `Session` per request.
    - In **production/running app**: opens a new session, yields it to the route handler, then **commits on success** and **rolls back on error**.
    - In **tests**: is overridden in `tests/conftest.py` to reuse the transactional test session without committing.

- `app/database/db_helper.py`
  - `get_db_session()` – context manager used mainly in validators and utilities.
    - In **tests**: returns the injected test session and does **not** commit/rollback/close (the fixture handles the transaction and rollback).
    - In **production**: behaves like `get_db` – creates a new session, commits on success, rolls back on error and closes.

### Auth utilities

Located in `app/utilis/auth.py`:

- `verify_password()` / `get_password_hash()` – bcrypt-based password hashing/verification.
- `create_access_token()` – builds a JWT with:
  - `sub`: user id (string UUID)
  - `exp`: expiration timestamp
  - `type`: token type (e.g. `"access"`)
- `verify_token()` – validates the JWT (signature, expiry, and type).
- `get_current_session()` – **core FastAPI dependency** that:
  1. Extracts the Bearer token from the `Authorization` header.
  2. Verifies the JWT.
  3. Uses `get_db_session()` to look up a matching row in the `sessions` table.
  4. Checks server-side session expiration (based on `last_used_at` or `created_at`).
  5. Updates `last_used_at`.
  6. Returns the `Session` model instance.
- `get_current_user()` – FastAPI dependency that:
  1. Depends on `get_current_session` to validate the token/session.
  2. Uses `get_db_session()` to load and return the `User` model by `current_session.user_id`.

---

## Login Flow

**Endpoint:** `POST /auth/login`

- Route: `app/routers/web.py`

```python
@router.post("/auth/login", name="v1-auth-login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    return AuthController.login(db, request.email, request.password)
```

- Controller: `app/controllers/auth_controller.py`, method `AuthController.login`:

  1. Query user by email.
  2. Verify password using `verify_password`.
  3. Create a JWT via `create_access_token({"sub": str(user.id)})`.
  4. Create a `Session` row:

     ```python
     session = SessionModel(
         id=uuid4(),
         user_id=user.id,
         token=access_token,
         last_used_at=datetime.utcnow(),
     )

     db.add(session)
     db.flush()
     db.refresh(session)
     ```

  5. Return:

     ```json
     {
       "access_token": "<jwt>",
       "type": "Bearer",
       "user": {
         "id": "...",
         "name": "...",
         "surname": "...",
         "email": "..."
       }
     }
     ```

**Key point:** every successful login creates a **session record** tied to the specific JWT token.

---

## Request Authentication Flow

Any protected route that uses:

```python
current_user: User = Depends(get_current_user)
```

will go through the following logic in `get_current_user` (`app/utilis/auth.py`):

1. **Extract token**

   - Uses `HTTPBearer()` security scheme.
   - Reads `Authorization: Bearer <token>` header.

2. **Verify JWT**

   ```python
   payload = verify_token(token, token_type="access")
   user_id_str = payload.get("sub")
   ```

   - Checks signature, expiry, and `type == "access"`.

3. **Parse user id**

   - Converts `sub` into a `UUID`.

4. **Look up session**

   ```python
   db_session = db.query(SessionModel).filter(
       SessionModel.token == token,
       SessionModel.user_id == user_id,
   ).first()
   ```

   - If no session is found, raises `401 Session not found`.

5. **Check server-side session expiration**

   ```python
   expiration_time = db_session.last_used_at or db_session.created_at
   time_diff = now - expiration_time

   if time_diff.days >= SESSION_EXPIRE_DAYS:
       db.delete(db_session)
       db.flush()
       raise HTTPException(401, "Session has expired")
   ```

   - `SESSION_EXPIRE_DAYS` defines how many days a session can be inactive.
   - Even if the JWT is still cryptographically valid, the session can expire.

6. **Update last_used_at**

   ```python
   db_session.last_used_at = now
   db.flush()
   ```

   - Implements a **sliding expiration window**: each request refreshes the last-used timestamp.

7. **Load user**

   ```python
   user = db.query(User).filter(User.id == user_id).first()
   ```

   - If user does not exist, raises `401 User not found`.
   - Otherwise returns the `User` instance.

**Result:**

- Routes receive a fully-loaded `User` model as `current_user`.
- Authentication depends on **both** a valid JWT and a valid `Session` row.

---

## Logout Flow

**Endpoint:** `DELETE /auth/logout`

- Route in `app/routers/web.py`:

```python
@router.delete('/auth/logout', name="v1-auth-logout")
def logout(
    current_user: User = Depends(get_current_user),
    current_session: SessionModel = Depends(get_current_session),
    db: Session = Depends(get_db),
):
    return AuthController.logout(db, current_user, current_session)
```

- `get_current_session` (`app/utilis/auth.py`) verifies the JWT and returns the matching `Session` row.

- Controller: `AuthController.logout`:

  ```python
  db.delete(session)
  db.flush()
  ```

  - Deletes the session row for the current token.

**Effect:**

- The JWT might still be valid cryptographically, but:
  - `get_current_user` / `get_current_session` will no longer find a matching session row.
  - The API will treat that token as invalid (**server-side revocation**).

---

## Profile & "Me" Endpoints

### Get current user profile

**Endpoint:** `GET /auth/me`

```python
@router.get("/auth/me", name="v1-auth-me")
def get_me(current_user: User = Depends(get_current_user)):
    return ProfileController.get_me(current_user)
```

- Relies on `get_current_user` for authentication.
- `ProfileController.get_me` just returns selected user fields as JSON.

### Update profile

**Endpoint:** `PUT /profile/update`

```python
@router.put("/profile/update", name="v1-profile-update")
def update_profile(
    request: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ProfileController.update(current_user, request.name, request.surname, request.email, db)
```

- Auth:
  - Uses `get_current_user` (JWT + session).
- Data:
  - `ProfileUpdateRequest` Pydantic model.
- DB:
  - Uses injected `db: Session` and `db.flush()` according to the database guide.

### Update password

**Endpoint:** `PUT /profile/password/update`

```python
@router.put("/profile/password/update", name="v1-profile-password-update")
def update_password(
    request: ProfilePasswordUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ProfileController.update_password(current_user, request.old_password, request.password, request.password_confirm, db)
```

- Auth and DB access follow the same patterns as above.
- `ProfileController.update_password` ensures:
  - Old password is correct.
  - New password is different.
  - Password is stored hashed via `get_password_hash`.

---

## Summary

- **Login**
  - Validates credentials.
  - Creates a **JWT** and a **session row** linked to it.

- **Authenticated requests**
  - Validate JWT.
  - Require a matching `Session` row.
  - Enforce server-side session expiration with `SESSION_EXPIRE_DAYS`.
  - Update `last_used_at` for sliding expiration.

- **Logout**
  - Deletes the session row for the current token.
  - Effectively revokes that token.

This design combines the advantages of JWT (stateless verification) with the control of server-side sessions (revocation, inactivity timeout, tracking).
