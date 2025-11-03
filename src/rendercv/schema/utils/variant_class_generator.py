from typing import Any, Literal

import pydantic

__all__ = ["create_variant_class"]


def create_variant_class[T: pydantic.BaseModel](
    variant_name: str,
    defaults: dict[str, Any],
    base_class: type[T],
    discriminator_field: str,
    class_name_suffix: str,
    module_name: str,
) -> type[T]:
    """Dynamically create a variant Pydantic model class with the given defaults.

    This is a general-purpose function for creating Pydantic model variants
    from a base class with overridden field defaults. It supports:
    - Simple field overrides (strings, numbers, lists, etc.)
    - Recursive deep merging of nested Pydantic models
    - Automatic conversion of discriminator fields to Literal types
    - Preservation of field metadata (description, title)

    Args:
        variant_name: Name of the variant. Used to generate the class name (converted to
            PascalCase)
        defaults: Dictionary of field names to default values. Supports nested dicts for
            partial updates of nested models
        base_class: The base Pydantic model class to inherit from
        discriminator_field: Name of the discriminator field. This field will be
            converted to a Literal type with the variant value
        class_name_suffix: Suffix for the generated class name.
        module_name: Module name for the generated class.

    Returns:
        A dynamically created Pydantic model class that inherits from `base_class` with
        all field defaults applied from the defaults dictionary
    """
    # Step 1: Validate all fields exist in `base_class`
    validate_defaults_against_base(defaults, base_class, variant_name)

    # Step 2: Build field specifications for each override.
    field_specs: dict[str, Any] = {}
    base_fields = base_class.model_fields

    for field_name, default_value in defaults.items():
        base_field_info = base_fields[field_name]

        # Handle discriminator field
        if field_name == discriminator_field:
            field_specs[field_name] = create_discriminator_field_spec(
                default_value, base_field_info
            )
        # Handle nested objects (dict values)
        elif isinstance(default_value, dict):
            field_specs[field_name] = create_nested_field_spec(
                default_value, base_field_info
            )
        # Handle simple fields
        else:
            field_specs[field_name] = create_simple_field_spec(
                default_value, base_field_info
            )

    # Step 3: Generate the class name
    class_name = generate_class_name(variant_name, class_name_suffix)

    # Step 4: Create and return the dynamic model
    return pydantic.create_model(
        class_name,
        __base__=base_class,
        __module__=module_name,
        **field_specs,
    )


def validate_defaults_against_base(
    defaults: dict[str, Any],
    base_class: type[pydantic.BaseModel],
    variant_name: str,
) -> None:
    """Validate that all fields in defaults exist in the base model.

    Args:
        defaults: Dictionary of field names to default values
        base_class: The base Pydantic model class
        variant_name: Name of the variant (for error messages)

    Raises:
        ValueError: If any field in defaults is not defined in base_class
    """
    base_fields = base_class.model_fields

    for field_name in defaults:
        if field_name not in base_fields:
            message = (
                f"Field '{field_name}' in defaults for '{variant_name}' "
                f"is not defined in {base_class.__name__}"
            )
            raise ValueError(message)


def generate_class_name(variant_name: str, class_name_suffix: str) -> str:
    """Convert snake_case variant name to PascalCase class name with suffix.

    Args:
        variant_name: Snake_case name
        class_name_suffix: Suffix to append

    Returns:
        PascalCase class name with suffix
    """
    # Convert snake_case to PascalCase: my_variant_name -> MyVariantName
    # Instead of title(), just capitalize first letter of each word
    pascal_case = "".join(word.capitalize() for word in variant_name.split("_"))
    return f"{pascal_case}{class_name_suffix}"


def update_description_with_new_default(
    original_description: str | None,
    old_default: Any,
    new_default: Any,
) -> str | None:
    """Update field description to reflect new default value.

    If the description contains the string representation of the old default value,
    replace it with the string representation of the new default value.

    Args:
        original_description: Original field description
        old_default: Old default value
        new_default: New default value to replace with

    Returns:
        Updated description or None if no description exists
    """
    if original_description is None:
        return None

    # Simple string replacement of old default with new default
    old_default_str = str(old_default)
    new_default_str = str(new_default)

    return original_description.replace(f"`{old_default_str}`", f"`{new_default_str}`")


def create_discriminator_field_spec(
    discriminator_value: Any,
    base_field_info: pydantic.fields.FieldInfo,
) -> tuple[Any, pydantic.fields.FieldInfo]:
    """Create field spec for a discriminator field (converts to Literal type).

    Args:
        discriminator_value: The value for the discriminator
        base_field_info: The base model's field info for this field

    Returns:
        Tuple of (Literal type annotation, Field with default value)
    """
    field_annotation = Literal[discriminator_value]  # type: ignore

    # Update description with new default value
    updated_description = update_description_with_new_default(
        base_field_info.description,
        base_field_info.default,
        discriminator_value,
    )

    new_field = pydantic.Field(
        default=discriminator_value,
        description=updated_description,
        title=base_field_info.title,
    )
    return (field_annotation, new_field)


def deep_merge_nested_object[T: pydantic.BaseModel](
    base_nested_obj: T,
    updates: dict[str, Any],
) -> T:
    """Recursively merge nested dictionary updates into a Pydantic model instance.

    This function supports arbitrary nesting depth. For each key in updates:
    - If the value is a dict and the corresponding field is a Pydantic model,
      recursively merge it
    - Otherwise, apply the value directly

    Args:
        base_nested_obj: The base Pydantic model instance to merge into
        updates: Dictionary of updates to apply (supports nested dicts)

    Returns:
        A new Pydantic model instance with updates applied
    """
    # Build the final update dict by recursively merging nested objects
    merged_updates: dict[str, Any] = {}

    for key, value in updates.items():
        # Check if this is a nested dict that should be recursively merged
        if isinstance(value, dict):
            # Get the current value of this field from base_nested_obj
            current_value = getattr(base_nested_obj, key, None)

            # If the current value is a Pydantic model, recursively merge
            if isinstance(current_value, pydantic.BaseModel):
                merged_updates[key] = deep_merge_nested_object(current_value, value)
            else:
                # Not a Pydantic model, just use the dict as-is
                merged_updates[key] = value
        else:
            # Simple value, use directly
            merged_updates[key] = value

    return base_nested_obj.model_copy(update=merged_updates)


def create_nested_field_spec(
    default_value: dict[str, Any],
    base_field_info: pydantic.fields.FieldInfo,
) -> tuple[Any, pydantic.fields.FieldInfo]:
    """Create field spec for a nested Pydantic model with partial overrides.

    This handles the case where default_value is a dict that should be merged into a
    nested Pydantic model field.

    Args:
        default_value: Dictionary of updates to apply to the nested model
        base_field_info: The base model's field info for this field

    Returns:
        Tuple of (field annotation, Field with merged default)
    """
    # Get the base nested object - could be from default or default_factory
    base_nested_obj: pydantic.BaseModel | None = None

    if base_field_info.default_factory is not None:
        # Create an instance using the factory
        # Type ignore needed because default_factory is a generic callable
        base_nested_obj = base_field_info.default_factory()  # pyright: ignore[reportCallIssue]
    elif isinstance(base_field_info.default, pydantic.BaseModel):
        # The default is already a Pydantic model instance
        base_nested_obj = base_field_info.default

    if base_nested_obj is not None:
        # We have a Pydantic model to merge with
        modified_nested = deep_merge_nested_object(base_nested_obj, default_value)

        new_field = pydantic.Field(
            default=modified_nested,
            description=base_field_info.description,
            title=base_field_info.title,
        )
    else:
        # No Pydantic model found, just use the dict directly
        # (This should be rare - it means the field type is just dict)
        new_field = pydantic.Field(
            default=default_value,
            description=base_field_info.description,
            title=base_field_info.title,
        )

    return (base_field_info.annotation, new_field)  # pyright: ignore[reportReturnType]


def create_simple_field_spec(
    default_value: Any,
    base_field_info: pydantic.fields.FieldInfo,
) -> tuple[Any, pydantic.fields.FieldInfo]:
    """Create field spec for a simple field (non-nested, non-discriminator).

    Args:
        default_value: The default value for this field
        base_field_info: The base model's field info for this field

    Returns:
        Tuple of (field annotation, Field with default value)
    """
    # Update description with new default value
    updated_description = update_description_with_new_default(
        base_field_info.description,
        base_field_info.default,
        default_value,
    )

    new_field = pydantic.Field(
        default=default_value,
        description=updated_description,
        title=base_field_info.title,
    )
    return (base_field_info.annotation, new_field)
