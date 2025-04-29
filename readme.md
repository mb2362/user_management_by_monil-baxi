# [Fix] TypeError: 'username' is an invalid keyword argument for User in `test_user_profile_pic.py` #8

## Description

Several tests in `tests/test_services/test_user_profile_pic.py` are currently **failing** with the following error:

```
TypeError: 'username' is an invalid keyword argument for User
```

This occurs in the following tests:
- `test_upload_profile_picture`
- `test_upload_profile_picture_invalid_format`
- `test_upload_profile_picture_large_file`
- `test_upload_profile_picture_minio_error`

The error suggests that the `User` model is not properly accepting the `username` field during object instantiation, even though the `User` model **does define** `username` correctly:
```python
username: Mapped[str] = Column(String(100), nullable=True)
```
in `app/models/user_model.py`.

Upon reviewing the `User` model, the field is mapped correctly to the database schema.

---

## Steps to Reproduce

1. Run the test suite:
    ```bash
    pytest tests/test_services/test_user_profile_pic.py
    ```
2. Observe the `TypeError` during execution of the affected tests.

---

## Expected Behavior

- The `User` model should **accept `username`** as a valid keyword argument when creating instances.
- The tests should **pass without raising TypeErrors**.

---

## Action Items

- [ ] Re-run the tests to confirm the fix.
- [ ] Close this issue after successful verification.

---

## Related Files
- `app/models/user_model.py`
- `tests/test_services/test_user_profile_pic.py`

---
