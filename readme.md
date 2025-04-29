# [Fix] User Role Assignment During User Creation

## Problem Description

The current implementation of user creation allows assigning any arbitrary role without validating against supported roles.
This can lead to security vulnerabilities and undefined behavior if invalid roles are assigned.

Examples of issues:
- A user could be assigned a non-existent role like `"superhero"`.
- The system assigns ADMIN role based on user count (e.g., first user becomes ADMIN), which is fragile and not scalable.

## Steps to Reproduce

1. Create a new user and manually set an invalid role in the request payload.
2. Observe that the user is created with the invalid role.
3. Create multiple users and notice that role assignment depends on user count.

## Solution

### 1. Role Validation
- Introduce strict validation during user creation.
- Only allow roles from a predefined Enum (`UserRole`), e.g., `ADMIN`, `AUTHENTICATED`, `MANAGER`.
- Reject requests with invalid role values and return an appropriate error.

### 2. Refactor Role Assignment Logic
- Remove logic that assigns the ADMIN role based on total user count.
- Instead, rely on an explicit and validated role assignment.

### 3. Future-Proofing
- Introduce a role management system in the future to manage allowed roles dynamically.
- This will help with scaling as more roles or permissions are introduced.

## Example Validation

```python
from app.models.enums import UserRole
from fastapi import HTTPException

def validate_role(role: str) -> UserRole:
    try:
        return UserRole(role)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid role specified.")
```

During user creation, call `validate_role(payload.role)` before proceeding.

## Impact

- Prevents unauthorized or unsupported roles from being assigned.
- Increases system stability and security.
- Lays the groundwork for future role and permission management.

---