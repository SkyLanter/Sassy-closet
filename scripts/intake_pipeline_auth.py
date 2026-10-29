"""Authorization header for machine reads of the intake mã list.

The value comes from the environment. This module never prints it.

Local auto-list run.sh is not in this repo. Add this one flag to the curl
that GETs the mã list. Do not paste the secret into the script:

    -H "Authorization: Bearer ${INTAKE_PIPELINE_SECRET}"

The Vercel intake project uses the same variable name. See
``sassy-closet/docs/INTAKE_PIPELINE.md``.
"""

from __future__ import annotations

import os

INTAKE_PIPELINE_SECRET_ENV = "INTAKE_PIPELINE_SECRET"
MIN_LENGTH = 24
MAX_LENGTH = 256


def secret_usable(secret: str) -> bool:
    """Same shape the intake server accepts: 24–256 printable ASCII chars, no spaces."""
    if len(secret) < MIN_LENGTH or len(secret) > MAX_LENGTH:
        return False
    return all(33 <= ord(char) <= 126 for char in secret)


def authorization_headers() -> dict[str, str]:
    """Bearer header when the env is usable. Empty dict when it is not."""
    secret = os.environ.get(INTAKE_PIPELINE_SECRET_ENV, "").strip()
    if not secret_usable(secret):
        return {}
    return {"Authorization": f"Bearer {secret}"}
