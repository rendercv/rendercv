from collections.abc import Callable
from typing import Any, Literal, cast

import pydantic
from pydantic.fields import FieldInfo

from rendercv.exception import RenderCVInternalError

type FieldSpec = tuple[type[Any], FieldInfo]


def create_variant_pydantic_model[T: pydantic.BaseModel](
    variant_name: str,
    defaults: dict[str, Any],
    base_class: type[T],
    discriminator_field: str,
    class_name_suffix: str,
    module_name: str,
) -> type[T]:
    """Create a Pydantic model variant with customized field defaults.

    Handles three override types:
    - Discriminator fields: converted to Literal types
    - Nested dicts: deep-merged into nested Pydantic models
    - Simple values: direct default replacement

    Args:
        variant_name: Snake_case name (e.g., "modern_cv") → class name "ModernCvTheme"
        defaults: Field overrides. Nested dicts enable partial updates.
        base_class: Base model to inherit from
        discriminator_field: Field to constrain as Literal for tagged unions
        class_name_suffix: Appended to generated class name
        module_name: Module path for the generated class

    Returns:
        New model class with all overrides applied
    """
    validate_defaults_against_base(defaults, base_class, variant_name)

    field_specs: dict[str, Any] = {}
    base_fields = base_class.model_fields

    for field_name, default_value in defaults.items():
        base_field_info = base_fields[field_name]

        if field_name == discriminator_field:
            field_specs[field_name] = create_discriminator_field_spec(
                default_value, base_field_info
            )
        elif isinstance(default_value, dict):
            field_specs[field_name] = create_nested_field_spec(
                default_value, base_field_info
            )
        else:
            field_specs[field_name] = create_simple_field_spec(
                default_value, base_field_info
            )

    class_name = generate_model_name(variant_name, class_name_suffix)

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
            raise RenderCVInternalError(message)


def generate_model_name(variant_name: str, class_name_suffix: str) -> str:
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
    base_field_info: FieldInfo,
) -> FieldSpec:
    """Create field spec for a discriminator field (converts to Literal type).

    Args:
        discriminator_value: The value for the discriminator
        base_field_info: The base model's field info for this field

    Returns:
        Tuple of (Literal type annotation, Field with default value)
    """
    field_annotation = Literal[discriminator_value]

    # Update description with new default value
    updated_description = update_description_with_new_default(
        base_field_info.description,
        base_field_info.default,
        discriminator_value,
    )

    new_field = cast(
        FieldInfo,
        pydantic.Field(
            default=discriminator_value,
            description=updated_description,
            title=base_field_info.title,
        ),
    )
    return (cast(type[Any], field_annotation), new_field)


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


def create_nested_model_variant_model(
    base_model_class: type[pydantic.BaseModel],
    updates: dict[str, Any],
) -> type[pydantic.BaseModel]:
    """Create a variant class for a nested model with updated field descriptions.

    Recursively processes nested updates to ensure field descriptions are updated
    at all levels of nesting.

    Args:
        base_model_class: The base nested model class
        updates: Dictionary of field updates (can contain nested dicts)

    Returns:
        New model class with updated field descriptions and defaults
    """
    field_specs: dict[str, Any] = {}
    base_fields = base_model_class.model_fields

    for field_name, new_value in updates.items():
        if field_name not in base_fields:
            # Skip fields that don't exist in the base model
            continue

        base_field_info = base_fields[field_name]

        if isinstance(new_value, dict):
            # Check if this field is a nested Pydantic model
            nested_obj = None
            if base_field_info.default_factory is not None:
                factory = cast(Callable[[], Any], base_field_info.default_factory)
                nested_obj = factory()
            elif isinstance(base_field_info.default, pydantic.BaseModel):
                nested_obj = base_field_info.default

            if nested_obj is not None and isinstance(nested_obj, pydantic.BaseModel):
                # Recursively create nested field spec
                field_specs[field_name] = create_nested_field_spec(
                    new_value, base_field_info
                )
            else:
                # Not a nested model, just a dict field - treat as simple value
                field_specs[field_name] = create_simple_field_spec(
                    new_value, base_field_info
                )
        else:
            # Simple value - update description
            field_specs[field_name] = create_simple_field_spec(
                new_value, base_field_info
            )

    # Create variant class inheriting from base
    return pydantic.create_model(
        base_model_class.__name__,
        __base__=base_model_class,
        __module__=base_model_class.__module__,
        **field_specs,
    )


def create_nested_field_spec(
    default_value: dict[str, Any],
    base_field_info: FieldInfo,
) -> FieldSpec:
    """Create field spec for a nested Pydantic model with partial overrides.

    Creates a variant class for the nested model to ensure field descriptions
    are updated to reflect new default values.

    Args:
        default_value: Dictionary of updates to apply to the nested model
        base_field_info: The base model's field info for this field

    Returns:
        Tuple of (variant class annotation, Field with default_factory)
    """
    # Get the base nested object - could be from default or default_factory
    base_nested_obj: pydantic.BaseModel | None = None

    if base_field_info.default_factory is not None:
        # Create an instance using the factory
        # Cast to proper callable type to satisfy type checker
        factory = cast(Callable[[], Any], base_field_info.default_factory)
        base_nested_obj = cast(pydantic.BaseModel, factory())
    elif isinstance(base_field_info.default, pydantic.BaseModel):
        # The default is already a Pydantic model instance
        base_nested_obj = base_field_info.default

    if base_nested_obj is not None:
        # Create a variant class with updated field specs and descriptions
        base_model_class = type(base_nested_obj)
        variant_class = create_nested_model_variant_model(
            base_model_class, default_value
        )

        new_field = cast(
            FieldInfo,
            pydantic.Field(
                default_factory=variant_class,
                description=base_field_info.description,
                title=base_field_info.title,
            ),
        )

        return (variant_class, new_field)
    # No Pydantic model found, just use the dict directly
    # (This should be rare - it means the field type is just dict)
    new_field = cast(
        FieldInfo,
        pydantic.Field(
            default=default_value,
            description=base_field_info.description,
            title=base_field_info.title,
        ),
    )

    return (
        cast(type[Any], base_field_info.annotation),
        new_field,
    )


def create_simple_field_spec(
    default_value: Any,
    base_field_info: FieldInfo,
) -> FieldSpec:
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

    new_field = cast(
        FieldInfo,
        pydantic.Field(
            default=default_value,
            description=updated_description,
            title=base_field_info.title,
        ),
    )
    return (cast(type[Any], base_field_info.annotation), new_field)
