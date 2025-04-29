# Docker Build - libc-bin Version Downgrade Issue

## Problem

During Docker builds based on **Debian bookworm**, installation of a specific version of `libc-bin` (`2.36-9+deb12u7`) **fails** with the following error:

```
E: Packages were downgraded and -y was used without --allow-downgrades.
failed to solve: process "/bin/sh -c apt-get update && apt-get install -y libc-bin=2.36-9+deb12u7 && apt-get clean && rm -rf /var/lib/apt/lists/*" did not complete successfully: exit code: 100
```

This happens because `apt-get install -y` **does not allow downgrades** by default, and the version being installed is considered a downgrade compared to the newer version available in the base image.

## Root Cause

- `apt-get install -y` **requires `--allow-downgrades`** when installing an older package version than what's currently installed.
- Without `--allow-downgrades`, `apt` aborts the installation with an error code `100`, causing the Docker build to fail.
- This blocked CI/CD pipelines and deployments relying on GitHub Actions.

## Solution

**Add `--allow-downgrades`** to the `apt-get install` command in the Dockerfile.

### Changes Made:

- In **Base Stage** (line 18):
  ```dockerfile
  && apt-get install -y --allow-downgrades libc-bin=2.36-9+deb12u7 \
  ```
- In **Final Stage** (line 33):
  ```dockerfile
  RUN apt-get update && apt-get install -y --allow-downgrades libc-bin=2.36-9+deb12u7 \
  ```

This ensures the build proceeds even when a downgrade is necessary.

## Recommendations

- **Version pinning** (`libc-bin=2.36-9+deb12u7`) should be used carefully to avoid compatibility issues with newer base images.
- Consider removing hard pins unless absolutely necessary.
- If version control is required, periodically **review pinned versions** to avoid security vulnerabilities or incompatibilities.
