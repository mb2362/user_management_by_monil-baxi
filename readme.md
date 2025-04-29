# [Fix] JWT Token Creation and Decoding Issue #10

## Description

In the current implementation of JWT token creation and decoding:

- In the `create_access_token` function:
  - The `user_id` is being assigned from `data["sub"]`.
  - There is no explicit check for whether the `sub` key exists, which could lead to runtime errors if the key is missing.

- In the `decode_token` function:
  - Errors such as `ExpiredSignatureError` or `InvalidTokenError` are not specifically handled.
  - Currently, the function returns `None` for **any** error, which makes debugging token-related issues difficult.

Improving these areas will enhance the robustness and maintainability of the authentication system.

## Proposed Solution

1. **Enhance `create_access_token`**:
    - Add an explicit check to ensure the `"sub"` key exists in the `data` dictionary.
    - Raise a meaningful exception if `"sub"` is missing.

    ```python
    if "sub" not in data:
        raise ValueError("Missing 'sub' field in token payload.")
    ```

2. **Improve `decode_token` with Specific Error Handling**:
    - Catch and handle specific JWT errors:
      - `jwt.ExpiredSignatureError`: Token has expired.
      - `jwt.InvalidTokenError`: General token error (e.g., tampered token).
    - Return more informative error messages or raise appropriate exceptions.

    ```python
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        user_role: str = payload.get("role")
        if user_id is None:
            raise credentials_exception
        return {"user_id": user_id, "user_role": user_role}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token.")
    ```

## Benefits

- Prevents hidden bugs from missing fields during token creation.
- Provides clear feedback when token decoding fails.
- Improves debugging experience for developers and API consumers.
- Enhances overall security and reliability of the authentication process.