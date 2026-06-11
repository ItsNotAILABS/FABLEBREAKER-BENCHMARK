"""
Validators for checking data integrity and schema compliance.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ValidationResult:
    """Result of a validation check."""
    valid: bool
    validator_id: str
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "validator_id": self.validator_id,
            "message": self.message,
            "details": self.details,
        }


class Validator:
    """Base validator class."""

    def __init__(self, validator_id: str) -> None:
        self.validator_id = validator_id

    def validate(self, data: Any) -> ValidationResult:
        return ValidationResult(valid=True, validator_id=self.validator_id)


class SchemaValidator(Validator):
    """Validates data against a schema definition."""

    def __init__(self, validator_id: str, required_fields: list[str] | None = None, field_types: dict[str, type] | None = None) -> None:
        super().__init__(validator_id)
        self.required_fields = required_fields or []
        self.field_types = field_types or {}

    def validate(self, data: Any) -> ValidationResult:
        if not isinstance(data, dict):
            return ValidationResult(
                valid=False, validator_id=self.validator_id,
                message="Expected dict, got " + type(data).__name__,
            )

        # Check required fields
        missing = [f for f in self.required_fields if f not in data]
        if missing:
            return ValidationResult(
                valid=False, validator_id=self.validator_id,
                message=f"Missing required fields: {missing}",
                details={"missing_fields": missing},
            )

        # Check field types
        type_errors: list[str] = []
        for field_name, expected_type in self.field_types.items():
            if field_name in data and not isinstance(data[field_name], expected_type):
                type_errors.append(
                    f"{field_name}: expected {expected_type.__name__}, got {type(data[field_name]).__name__}"
                )

        if type_errors:
            return ValidationResult(
                valid=False, validator_id=self.validator_id,
                message="Type validation errors",
                details={"type_errors": type_errors},
            )

        return ValidationResult(valid=True, validator_id=self.validator_id, message="Schema valid")


class HashValidator(Validator):
    """Validates SHA-256 hash integrity of data."""

    def __init__(self, validator_id: str = "hash-validator") -> None:
        super().__init__(validator_id)

    def validate_hash(self, data: Any, expected_hash: str) -> ValidationResult:
        """Validate that data produces the expected SHA-256 hash."""
        payload = json.dumps(data, sort_keys=True, separators=(",", ":"))
        actual_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

        if actual_hash == expected_hash:
            return ValidationResult(
                valid=True, validator_id=self.validator_id,
                message="Hash verification passed",
                details={"hash": actual_hash},
            )
        return ValidationResult(
            valid=False, validator_id=self.validator_id,
            message="Hash mismatch",
            details={"expected": expected_hash, "actual": actual_hash},
        )

    def validate(self, data: Any) -> ValidationResult:
        """Basic validation: just ensure data is hashable."""
        try:
            payload = json.dumps(data, sort_keys=True, separators=(",", ":"))
            hashlib.sha256(payload.encode("utf-8")).hexdigest()
            return ValidationResult(valid=True, validator_id=self.validator_id, message="Data is hashable")
        except (TypeError, ValueError) as exc:
            return ValidationResult(
                valid=False, validator_id=self.validator_id,
                message=f"Data cannot be hashed: {exc}",
            )


class ConstraintValidator(Validator):
    """Validates data against a set of constraints."""

    def __init__(self, validator_id: str = "constraint-validator") -> None:
        super().__init__(validator_id)
        self._constraints: list[tuple[str, Any]] = []

    def add_range(self, field: str, min_val: float | None = None, max_val: float | None = None) -> None:
        self._constraints.append(("range", {"field": field, "min": min_val, "max": max_val}))

    def add_required(self, field: str) -> None:
        self._constraints.append(("required", {"field": field}))

    def add_one_of(self, field: str, values: list[Any]) -> None:
        self._constraints.append(("one_of", {"field": field, "values": values}))

    def validate(self, data: Any) -> ValidationResult:
        if not isinstance(data, dict):
            return ValidationResult(valid=False, validator_id=self.validator_id, message="Expected dict")

        errors: list[str] = []
        for constraint_type, params in self._constraints:
            if constraint_type == "required":
                if params["field"] not in data:
                    errors.append(f"Missing required field: {params['field']}")
            elif constraint_type == "range":
                val = data.get(params["field"])
                if val is not None:
                    if params["min"] is not None and val < params["min"]:
                        errors.append(f"{params['field']} below minimum: {val} < {params['min']}")
                    if params["max"] is not None and val > params["max"]:
                        errors.append(f"{params['field']} above maximum: {val} > {params['max']}")
            elif constraint_type == "one_of":
                val = data.get(params["field"])
                if val is not None and val not in params["values"]:
                    errors.append(f"{params['field']} not in allowed values: {val}")

        if errors:
            return ValidationResult(
                valid=False, validator_id=self.validator_id,
                message="Constraint violations",
                details={"errors": errors},
            )
        return ValidationResult(valid=True, validator_id=self.validator_id, message="All constraints satisfied")
