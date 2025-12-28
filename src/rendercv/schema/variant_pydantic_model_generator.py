from collections.abc import Callable
from typing import Any, Literal, cast

import pydantic
from pydantic.fields import FieldInfo

from rendercv.exception import RenderCVInternalError

type FieldSpec = tuple[type[Any], FieldInfo]


def sanitize_defaults(value: Any) -> Any:
    """Recursively convert CommentedMap/CommentedSeq to dict/list.

    Why:
        ruamel.yaml returns custom types that behave like dict/list but confuse Pydantic
        and JSON schema generation. Stripping metadata ensures clean defaults.

    Args:
        value: The value to sanitize (can be nested dict/list structure).

    Returns:
        The sanitized value with standard Python types.
    """
    if isinstance(value, list):
        return [sanitize_defaults(v) for v in value]
    if isinstance(value, dict):
        return {k: sanitize_defaults(v) for k, v in value.items()}
    return value


def create_variant_pydantic_model[T: pydantic.BaseModel](
    variant_name: str,
    defaults: dict[str, Any],
    base_class: type[T],
    discriminator_field: str,
    class_name_suffix: str,
    module_name: str,
) -> type[T]:
    """Create Pydantic model variant with customized defaults.

    Why:
        Themes share common structure but differ in default colors, fonts,
        and spacing. Variant generation creates theme-specific classes that
        inherit validation logic while exposing different defaults in JSON schema.

    Example:
        ```py
        ModernTheme = create_variant_pydantic_model(
            variant_name="modern",
            defaults={"theme": "modern", "colors": {"primary": "#000"}},
            base_class=BaseTheme,
            discriminator_field="theme",
            class_name_suffix="Theme",
            module_name="rendercv.themes",
        )
        # Creates class "ModernTheme" with theme="modern" as Literal type
        ```

    Args:
        variant_name: Snake_case name for PascalCase conversion.
        defaults: Field overrides with nested dict support.
        base_class: Base model to inherit from.
        discriminator_field: Field to constrain as Literal for tagged unions.
        class_name_suffix: Appended to generated class name.
        module_name: Module path for the generated class.

    Returns:
        New model class with overrides applied.
    """
    validate_defaults_against_base(defaults, base_class, variant_name)

    # Sanitize defaults to remove ruamel.yaml metadata
    defaults = sanitize_defaults(defaults)

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

    Why:
        Typos in theme definitions cause silent failures. Early validation
        prevents variants with undefined fields from being created.

    Args:
        defaults: Field overrides to validate.
        base_class: Base model defining valid fields.
        variant_name: Variant identifier for error messages.
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
        variant_name: Snake_case name.
        class_name_suffix: Suffix to append.

    Returns:
        PascalCase class name with suffix.
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

    Why:
        JSON schema descriptions must show current defaults. When variants
        override defaults, descriptions need updating so IDE tooltips display
        accurate information.

    Args:
        original_description: Original field description.
        old_default: Old default value.
        new_default: New default value to replace with.

    Returns:
        Updated description or None if no description exists.
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
    """Create field spec for discriminator field with Literal type constraint.

    Why:
        Pydantic discriminated unions require Literal types for routing.
        Converting theme="classic" to Literal["classic"] enables automatic
        theme class selection during validation.

    Args:
        discriminator_value: Value for the discriminator.
        base_field_info: Base model's field info.

    Returns:
        Tuple of Literal type annotation and Field with default value.
    """
    field_annotation = Literal[discriminator_value]  # ty: ignore[invalid-type-form]

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
    """Recursively merge nested dictionary updates into Pydantic model instance.

    Why:
        Theme variants often override only specific nested fields like
        `colors.primary` while keeping other color defaults. Deep merge
        enables partial updates without requiring full object replacement.

    Args:
        base_nested_obj: Base model instance to merge into.
        updates: Dictionary updates with arbitrary nesting depth.

    Returns:
        New model instance with updates applied.
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
    """Create variant class for nested model with updated field descriptions.

    Why:
        Nested field defaults must reflect in JSON schema for accurate IDE
        tooltips. Creating variant classes ensures descriptions update at all
        nesting levels, not just the top level.

    Args:
        base_model_class: Base nested model class.
        updates: Field updates with potential nested dicts.

    Returns:
        New model class with updated descriptions and defaults.
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
    """Create field spec for nested Pydantic model with partial overrides.

    Why:
        Nested model fields require variant classes to preserve accurate JSON
        schema metadata. This ensures nested defaults appear correctly in IDE
        autocompletion and documentation.

    Args:
        default_value: Dictionary updates to apply to nested model.
        base_field_info: Base model's field info.

    Returns:
        Tuple of variant class annotation and Field with default_factory.
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
    """Create field spec for simple field with updated default.

    Args:
        default_value: New default value for field.
        base_field_info: Base model's field info.

    Returns:
        Tuple of field annotation and Field with default value.
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
