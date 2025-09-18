"""Test module to demonstrate coding style compliance.

This module showcases the coding standards defined in CODING_STYLE.md,
including proper function organization, type hints, and formatting.
"""

import json
from pathlib import Path
from typing import Any


def process_user_data(
    user_id: int,
    name: str,
    email: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Process user data and generate a comprehensive user profile.

    This function acts as the main orchestrator, calling helper functions
    to validate, format, and save user data.

    Args:
        user_id: Unique identifier for the user
        name: Full name of the user
        email: Email address for the user
        metadata: Optional metadata dictionary

    Returns:
        Dictionary containing the processed user profile
    """
    validated_data = _validate_user_input(
        user_id=user_id,
        name=name,
        email=email,
    )

    formatted_profile = _format_user_profile(
        validated_data=validated_data,
        metadata=metadata,
    )

    saved_profile = _save_user_profile(
        profile=formatted_profile,
    )

    return saved_profile


def _validate_user_input(
    user_id: int,
    name: str,
    email: str,
) -> dict[str, Any]:
    """Validate user input data according to business rules.

    Args:
        user_id: User identifier to validate
        name: Name to validate
        email: Email to validate

    Returns:
        Dictionary with validated user data

    Raises:
        ValueError: If any validation fails
    """
    if user_id <= 0:
        raise ValueError(f"Invalid user_id: {user_id}")

    if not _is_valid_email(email=email):
        raise ValueError(f"Invalid email format: {email}")

    if not _is_valid_name(name=name):
        raise ValueError(f"Invalid name format: {name}")

    return {
        "user_id": user_id,
        "name": name.strip().title(),
        "email": email.lower().strip(),
    }


def _is_valid_email(email: str) -> bool:
    """Check if email format is valid.

    Args:
        email: Email string to validate

    Returns:
        True if email is valid, False otherwise
    """
    return "@" in email and "." in email.split("@")[1]


def _is_valid_name(name: str) -> bool:
    """Check if name format is valid.

    Args:
        name: Name string to validate

    Returns:
        True if name is valid, False otherwise
    """
    return len(name.strip()) >= 2 and name.strip().replace(" ", "").isalpha()


def _format_user_profile(
    validated_data: dict[str, Any],
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Format user data into a standardized profile structure.

    Args:
        validated_data: Previously validated user data
        metadata: Optional metadata to include

    Returns:
        Formatted user profile dictionary
    """
    profile = {
        "id": validated_data["user_id"],
        "personal_info": _format_personal_info(
            name=validated_data["name"],
            email=validated_data["email"],
        ),
        "created_at": _get_current_timestamp(),
    }

    if metadata:
        profile["metadata"] = _sanitize_metadata(metadata=metadata)

    return profile


def _format_personal_info(name: str, email: str) -> dict[str, str]:
    """Format personal information section.

    Args:
        name: User's formatted name
        email: User's formatted email

    Returns:
        Dictionary with formatted personal information
    """
    return {
        "full_name": name,
        "email_address": email,
        "display_name": name.split()[0],
    }


def _get_current_timestamp() -> str:
    """Get current timestamp in ISO format.

    Returns:
        ISO formatted timestamp string
    """
    from datetime import datetime

    return datetime.now().isoformat()


def _sanitize_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    """Sanitize metadata by removing sensitive keys.

    Args:
        metadata: Raw metadata dictionary

    Returns:
        Sanitized metadata dictionary
    """
    sensitive_keys = {"password", "token", "secret", "key"}

    return {
        key: value
        for key, value in metadata.items()
        if key.lower() not in sensitive_keys
    }


def _save_user_profile(profile: dict[str, Any]) -> dict[str, Any]:
    """Save user profile to file system.

    Args:
        profile: User profile to save

    Returns:
        Profile with added save metadata
    """
    output_path = _get_output_path(user_id=profile["id"])

    _write_profile_to_file(
        profile=profile,
        file_path=output_path,
    )

    return {
        **profile,
        "saved_to": str(output_path),
        "status": "saved",
    }


def _get_output_path(user_id: int) -> Path:
    """Generate output file path for user profile.

    Args:
        user_id: User identifier

    Returns:
        Path object for the output file
    """
    output_dir = Path("profiles")
    output_dir.mkdir(exist_ok=True)

    return output_dir / f"user_{user_id}.json"


def _write_profile_to_file(
    profile: dict[str, Any],
    file_path: Path,
) -> None:
    """Write profile data to JSON file.

    Args:
        profile: User profile data
        file_path: Target file path
    """
    with file_path.open(mode="w", encoding="utf-8") as file:
        json.dump(
            obj=profile,
            fp=file,
            indent=2,
            ensure_ascii=False,
        )