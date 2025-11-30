from typing import Any, get_args

import pydantic
import pytest

from rendercv.exception import RenderCVInternalError
from rendercv.schema.variant_pydantic_model_generator import (
    create_discriminator_field_spec,
    create_nested_field_spec,
    create_simple_field_spec,
    create_variant_pydantic_model,
    deep_merge_nested_object,
    generate_model_name,
    update_description_with_new_default,
    validate_defaults_against_base,
)


class SimpleModel(pydantic.BaseModel):
    discriminator: str = pydantic.Field(
        default="base", description="The discriminator field", title="Discriminator"
    )
    field1: str = pydantic.Field(
        default="default1", description="First field", title="Field 1"
    )
    field2: int = pydantic.Field(
        default=42, description="Second field", title="Field 2"
    )
    field3: list[str] = pydantic.Field(
        default=["a", "b"], description="Third field", title="Field 3"
    )


class Inner(pydantic.BaseModel):
    x: int = pydantic.Field(default=1, description="X value", title="X")
    y: int = pydantic.Field(default=2, description="Y value", title="Y")


class Middle(pydantic.BaseModel):
    inner: Inner = Inner()
    z: int = pydantic.Field(default=3, description="Z value", title="Z")


class NestedModel(pydantic.BaseModel):
    discriminator: str = pydantic.Field(
        default="base", description="Discriminator", title="Discriminator"
    )
    middle: Middle = Middle()
    simple: str = pydantic.Field(
        default="simple", description="Simple field", title="Simple"
    )


class NestedWithFactory(pydantic.BaseModel):
    value: str = "factory_default"
    count: int = 10


class ModelWithFactory(pydantic.BaseModel):
    discriminator: str = "base"
    nested: NestedWithFactory = pydantic.Field(
        default_factory=NestedWithFactory,
        description="Nested with factory",
        title="Nested Factory",
    )


@pytest.mark.parametrize(
    ("defaults", "variant_name", "expected_error", "match_pattern"),
    [
        pytest.param(
            {"field1": "new_value", "field2": 100},
            "test_variant",
            None,
            None,
            id="valid_fields",
        ),
        pytest.param(
            {"field1": "value", "invalid_field": "bad"},
            "test_variant",
            RenderCVInternalError,
            "Field 'invalid_field' in defaults",
            id="invalid_field_raises_error",
        ),
        pytest.param(
            {},
            "test_variant",
            None,
            None,
            id="empty_defaults",
        ),
        pytest.param(
            {"nonexistent": "value"},
            "my_variant",
            RenderCVInternalError,
            "SimpleModel",
            id="error_includes_model_name",
        ),
    ],
)
def test_validate_defaults_against_base(
    defaults: dict[str, Any],
    variant_name: str,
    expected_error: type[Exception] | None,
    match_pattern: str | None,
):
    if expected_error:
        with pytest.raises(expected_error, match=match_pattern):
            validate_defaults_against_base(defaults, SimpleModel, variant_name)
    else:
        validate_defaults_against_base(defaults, SimpleModel, variant_name)


@pytest.mark.parametrize(
    ("variant_name", "suffix", "expected_class_name"),
    [
        pytest.param("turkish", "Locale", "TurkishLocale", id="simple_name"),
        pytest.param(
            "sb2nov", "Theme", "Sb2novTheme", id="name_with_numbers_lowercase"
        ),
        pytest.param(
            "my_custom_variant",
            "Type",
            "MyCustomVariantType",
            id="multi_word_snake_case",
        ),
        pytest.param("single", "Suffix", "SingleSuffix", id="single_word"),
        pytest.param(
            "snake_case_name", "Model", "SnakeCaseNameModel", id="standard_snake_case"
        ),
        pytest.param(
            "already_pascal", "Class", "AlreadyPascalClass", id="pascal_case_input"
        ),
        pytest.param(
            "multiple_underscores", "X", "MultipleUnderscoresX", id="short_suffix"
        ),
        pytest.param("my_variant", "", "MyVariant", id="empty_suffix"),
    ],
)
def test_generate_model_name(variant_name, suffix, expected_class_name):
    result = generate_model_name(variant_name, suffix)
    assert result == expected_class_name


@pytest.mark.parametrize(
    "discriminator_value",
    [
        pytest.param("my_variant", id="string"),
        pytest.param(123, id="integer"),
        pytest.param(True, id="boolean"),
        pytest.param("special-chars-123", id="string_with_special_chars"),
    ],
)
def test_create_discriminator_field_spec(discriminator_value: Any):
    field_info = SimpleModel.model_fields["discriminator"]

    annotation, field = create_discriminator_field_spec(discriminator_value, field_info)

    # Check Literal type is created
    assert get_args(annotation) == (discriminator_value,)

    # Check default value is set
    assert field.default == discriminator_value

    # Check metadata is preserved
    assert field.description == "The discriminator field"
    assert field.title == "Discriminator"


class TestDeepMergeNestedObject:
    def test_shallow_merge(self):
        class Simple(pydantic.BaseModel):
            a: int = 1
            b: str = "original"

        base = Simple()
        updates = {"a": 100}

        result = deep_merge_nested_object(base, updates)

        assert result.a == 100
        assert result.b == "original"

    def test_deep_merge(self):
        class Inner(pydantic.BaseModel):
            x: int = 1
            y: int = 2

        class Middle(pydantic.BaseModel):
            inner: Inner = Inner()
            z: int = 3

        class Outer(pydantic.BaseModel):
            middle: Middle = Middle()
            top: str = "top"

        base = Outer()
        updates = {
            "middle": {
                "inner": {"x": 100},
                "z": 30,
            }
        }

        result = deep_merge_nested_object(base, updates)

        assert result.middle.inner.x == 100
        assert result.middle.inner.y == 2  # Preserved
        assert result.middle.z == 30
        assert result.top == "top"

    def test_dict_field(self):
        class WithDict(pydantic.BaseModel):
            data: dict[str, Any] = {
                "key": "value",
            }

        base = WithDict()
        updates = {"data": {"new_key": "new_value"}}

        result = deep_merge_nested_object(base, updates)

        assert result.data == {"new_key": "new_value"}

    def test_multiple_fields(self):
        class Multi(pydantic.BaseModel):
            field1: str = "a"
            field2: int = 1
            field3: bool = True

        base = Multi()
        updates = {
            "field1": "updated",
            "field2": 999,
        }

        result = deep_merge_nested_object(base, updates)

        assert result.field1 == "updated"
        assert result.field2 == 999
        assert result.field3 is True

    def test_empty_updates(self):
        class Simple(pydantic.BaseModel):
            value: int = 42

        base = Simple()
        updates: dict[str, Any] = {}

        result = deep_merge_nested_object(base, updates)

        assert result.value == 42
        assert result is not base

    def test_three_levels_deep(self):
        class Level3(pydantic.BaseModel):
            value: int = 1

        class Level2(pydantic.BaseModel):
            level3: Level3 = Level3()

        class Level1(pydantic.BaseModel):
            level2: Level2 = Level2()

        base = Level1()
        updates = {"level2": {"level3": {"value": 999}}}

        result = deep_merge_nested_object(base, updates)

        assert result.level2.level3.value == 999


class TestCreateNestedFieldSpec:
    def test_with_default(self):
        class Inner(pydantic.BaseModel):
            x: int = 1
            y: int = 2

        class Outer(pydantic.BaseModel):
            inner: Inner = Inner()

        field_info = Outer.model_fields["inner"]
        updates = {
            "x": 100,
        }

        annotation, field = create_nested_field_spec(updates, field_info)

        # Check that a variant class was created with default_factory
        assert field.default_factory is not None
        assert issubclass(field.default_factory, pydantic.BaseModel)  # pyright: ignore[reportArgumentType]

        # Instantiate to check default values
        instance = field.default_factory()
        assert isinstance(instance, Inner)
        assert instance.x == 100
        assert instance.y == 2

        # Check that the annotation is the variant class
        assert annotation == field.default_factory

    def test_with_default_factory(self):
        field_info = ModelWithFactory.model_fields["nested"]
        updates = {
            "value": "updated",
            "count": 20,
        }

        _, field = create_nested_field_spec(updates, field_info)

        # Check that a variant class was created with default_factory
        assert field.default_factory is not None
        assert issubclass(field.default_factory, pydantic.BaseModel)  # pyright: ignore[reportArgumentType]

        # Instantiate to check default values
        instance = field.default_factory()
        assert isinstance(instance, NestedWithFactory)
        assert instance.value == "updated"
        assert instance.count == 20

    def test_preserves_metadata(self):
        class Inner(pydantic.BaseModel):
            x: int = 1

        class Outer(pydantic.BaseModel):
            inner: Inner = pydantic.Field(
                default=Inner(), description="Inner model", title="Inner Title"
            )

        field_info = Outer.model_fields["inner"]
        updates = {"x": 50}

        _annotation, field = create_nested_field_spec(updates, field_info)

        assert field.description == "Inner model"
        assert field.title == "Inner Title"

    def test_partial_update(self):
        class Nested(pydantic.BaseModel):
            field1: str = "a"
            field2: str = "b"
            field3: str = "c"

        class Outer(pydantic.BaseModel):
            nested: Nested = Nested()

        field_info = Outer.model_fields["nested"]
        updates = {"field1": "updated"}

        _, field = create_nested_field_spec(updates, field_info)

        # Check that a variant class was created with default_factory
        assert field.default_factory is not None
        assert issubclass(field.default_factory, pydantic.BaseModel)  # pyright: ignore[reportArgumentType]

        # Instantiate to check default values
        instance = field.default_factory()
        assert isinstance(instance, Nested)
        assert instance.field1 == "updated"
        assert instance.field2 == "b"
        assert instance.field3 == "c"


@pytest.mark.parametrize(
    ("field_name", "new_value", "expected_annotation"),
    [
        pytest.param("field1", "new_string_value", str, id="string_field"),
        pytest.param("field2", 999, int, id="int_field"),
        pytest.param("field3", ["x", "y", "z"], list[str], id="list_field"),
    ],
)
def test_create_simple_field_spec(
    field_name: str, new_value: Any, expected_annotation: type
):
    field_info = SimpleModel.model_fields[field_name]

    annotation, field = create_simple_field_spec(new_value, field_info)

    # Check default value is set correctly
    assert field.default == new_value

    # Check annotation is preserved
    assert annotation == expected_annotation

    # Check metadata is preserved
    assert field.description is not None
    assert field.title is not None


class TestCreateVariantPydanticModel:
    def test_simple_fields(self):
        defaults = {
            "discriminator": "my_variant",
            "field1": "custom_value",
            "field2": 100,
        }

        VariantClass = create_variant_pydantic_model(
            variant_name="my_variant",
            defaults=defaults,
            base_class=SimpleModel,
            discriminator_field="discriminator",
            class_name_suffix="Model",
            module_name="test.module",
        )

        # Test class properties
        assert VariantClass.__name__ == "MyVariantModel"
        assert VariantClass.__module__ == "test.module"
        assert issubclass(VariantClass, SimpleModel)

        # Test instance
        instance = VariantClass()
        assert instance.discriminator == "my_variant"
        assert instance.field1 == "custom_value"
        assert instance.field2 == 100
        assert instance.field3 == ["a", "b"]  # Default preserved

    def test_nested_models(self):
        defaults = {
            "discriminator": "custom",
            "middle": {
                "inner": {"x": 100},
                "z": 30,
            },
            "simple": "updated",
        }

        VariantClass = create_variant_pydantic_model(
            variant_name="custom",
            defaults=defaults,
            base_class=NestedModel,
            discriminator_field="discriminator",
            class_name_suffix="Variant",
            module_name="test.nested",
        )

        instance = VariantClass()
        assert instance.discriminator == "custom"
        assert instance.middle.inner.x == 100
        assert instance.middle.inner.y == 2  # Preserved
        assert instance.middle.z == 30
        assert instance.simple == "updated"

    def test_discriminator_is_literal(self):
        class Base(pydantic.BaseModel):
            variant: str = "base"
            value: int = 1

        defaults = {
            "variant": "custom",
            "value": 42,
        }

        CustomClass = create_variant_pydantic_model(
            variant_name="custom",
            defaults=defaults,
            base_class=Base,
            discriminator_field="variant",
            class_name_suffix="Class",
            module_name="test",
        )

        # Get the field annotation
        field_info = CustomClass.model_fields["variant"]
        annotation = field_info.annotation

        # Check it's a Literal type with the correct value
        assert get_args(annotation) == ("custom",)

    def test_empty_defaults(self):
        defaults: dict[str, Any] = {}

        VariantClass = create_variant_pydantic_model(
            variant_name="empty",
            defaults=defaults,
            base_class=SimpleModel,
            discriminator_field="discriminator",
            class_name_suffix="Empty",
            module_name="test",
        )

        # Should create a valid class that inherits all defaults
        instance = VariantClass()
        assert instance.field1 == "default1"
        assert instance.field2 == 42

    @pytest.mark.parametrize(
        ("variant_name", "suffix", "expected_name"),
        [
            pytest.param("turkish", "Locale", "TurkishLocale", id="turkish_locale"),
            pytest.param("sb2nov", "Theme", "Sb2novTheme", id="sb2nov_theme"),
            pytest.param(
                "my_custom_name", "Type", "MyCustomNameType", id="custom_name_type"
            ),
        ],
    )
    def test_class_name_generation(
        self, variant_name: str, suffix: str, expected_name: str
    ):
        class Base(pydantic.BaseModel):
            disc: str = "base"

        VariantClass = create_variant_pydantic_model(
            variant_name=variant_name,
            defaults={"disc": variant_name},
            base_class=Base,
            discriminator_field="disc",
            class_name_suffix=suffix,
            module_name="test",
        )
        assert VariantClass.__name__ == expected_name

    def test_module_assignment(self):
        defaults = {
            "discriminator": "test",
        }

        VariantClass = create_variant_pydantic_model(
            variant_name="test",
            defaults=defaults,
            base_class=SimpleModel,
            discriminator_field="discriminator",
            class_name_suffix="Class",
            module_name="my.custom.module.path",
        )

        assert VariantClass.__module__ == "my.custom.module.path"

    def test_preserves_field_metadata(self):
        defaults = {
            "discriminator": "test",
            "field1": "new_value",
        }

        VariantClass = create_variant_pydantic_model(
            variant_name="test",
            defaults=defaults,
            base_class=SimpleModel,
            discriminator_field="discriminator",
            class_name_suffix="Class",
            module_name="test",
        )

        field_info = VariantClass.model_fields["field1"]
        assert field_info.description == "First field"
        assert field_info.title == "Field 1"

    def test_deep_nesting(self):
        class Level3(pydantic.BaseModel):
            value: int = 1

        class Level2(pydantic.BaseModel):
            level3: Level3 = Level3()

        class Level1(pydantic.BaseModel):
            disc: str = "base"
            level2: Level2 = Level2()

        defaults = {
            "disc": "deep",
            "level2": {
                "level3": {"value": 999},
            },
        }

        DeepVariant = create_variant_pydantic_model(
            variant_name="deep",
            defaults=defaults,
            base_class=Level1,
            discriminator_field="disc",
            class_name_suffix="Variant",
            module_name="test.deep",
        )

        instance = DeepVariant()
        assert instance.level2.level3.value == 999

    def test_multiple_nested_fields(self):
        class Nested1(pydantic.BaseModel):
            x: int = 1

        class Nested2(pydantic.BaseModel):
            y: int = 2

        class Multi(pydantic.BaseModel):
            disc: str = "base"
            nested1: Nested1 = Nested1()
            nested2: Nested2 = Nested2()

        defaults = {
            "disc": "multi",
            "nested1": {"x": 10},
            "nested2": {"y": 20},
        }

        MultiVariant = create_variant_pydantic_model(
            variant_name="multi",
            defaults=defaults,
            base_class=Multi,
            discriminator_field="disc",
            class_name_suffix="Variant",
            module_name="test",
        )

        instance = MultiVariant()
        assert instance.nested1.x == 10
        assert instance.nested2.y == 20

    @pytest.mark.parametrize(
        ("defaults", "variant_name", "match_pattern"),
        [
            pytest.param(
                {"discriminator": "test", "nonexistent_field": "value"},
                "test",
                "Field 'nonexistent_field'",
                id="invalid_field_name",
            ),
            pytest.param(
                {"bad_field": "value"},
                "test_variant",
                "'test_variant'",
                id="error_includes_variant_name",
            ),
            pytest.param(
                {"invalid": "value"},
                "test",
                "SimpleModel",
                id="error_includes_base_class_name",
            ),
        ],
    )
    def test_validation_errors(
        self, defaults: dict[str, Any], variant_name: str, match_pattern: str
    ):
        with pytest.raises(RenderCVInternalError, match=match_pattern):
            create_variant_pydantic_model(
                variant_name=variant_name,
                defaults=defaults,
                base_class=SimpleModel,
                discriminator_field="discriminator",
                class_name_suffix="Class",
                module_name="test",
            )

    def test_can_override_defaults_at_instantiation(self):
        class Base(pydantic.BaseModel):
            disc: str = "base"
            value: int = 1

        defaults = {
            "disc": "variant",
            "value": 100,
        }

        VariantClass = create_variant_pydantic_model(
            variant_name="variant",
            defaults=defaults,
            base_class=Base,
            discriminator_field="disc",
            class_name_suffix="Class",
            module_name="test",
        )

        # Default instance
        default_instance = VariantClass()
        assert default_instance.value == 100

        # Override at instantiation
        custom_instance = VariantClass(value=999)
        assert custom_instance.value == 999


class TestUpdateDescriptionWithNewDefault:
    @pytest.mark.parametrize(
        ("description", "old_default", "new_default", "expected"),
        [
            pytest.param(
                "The language of the locale. The default value is `english`.",
                "english",
                "turkish",
                "The language of the locale. The default value is `turkish`.",
                id="string_replacement",
            ),
            pytest.param(
                "The count value. The default value is `42`.",
                42,
                100,
                "The count value. The default value is `100`.",
                id="integer_replacement",
            ),
            pytest.param(
                "Enable feature X. The default value is `False`.",
                False,
                True,
                "Enable feature X. The default value is `True`.",
                id="boolean_replacement",
            ),
            pytest.param(
                "This field has no default value mentioned in backticks.",
                "old",
                "new",
                "This field has no default value mentioned in backticks.",
                id="no_backticks_unchanged",
            ),
            pytest.param(
                "",
                "old",
                "new",
                "",
                id="empty_string",
            ),
            pytest.param(
                "This is a long description.\n\nIt has multiple lines.\nThe default"
                " value is `old`.",
                "old",
                "new",
                "This is a long description.\n\nIt has multiple lines.\nThe default"
                " value is `new`.",
                id="multiline_description",
            ),
            pytest.param(
                "The value is `42`. Another mention: `42`.",
                42,
                100,
                "The value is `100`. Another mention: `100`.",
                id="multiple_occurrences",
            ),
            pytest.param(
                "Optional field. The default value is `None`.",
                None,
                "something",
                "Optional field. The default value is `something`.",
                id="null_value",
            ),
        ],
    )
    def test_updates_description(
        self, description: str, old_default: Any, new_default: Any, expected: str
    ):
        updated = update_description_with_new_default(
            description, old_default, new_default
        )
        assert updated == expected

    def test_with_none_description(self):
        updated = update_description_with_new_default(None, "old", "new")
        assert updated is None


@pytest.mark.parametrize(
    (
        "field_name",
        "field_type",
        "old_default",
        "new_default",
        "base_description",
        "expected_description",
    ),
    [
        pytest.param(
            "language",
            str,
            "english",
            "turkish",
            "The language of the locale. The default value is `english`.",
            "The language of the locale. The default value is `turkish`.",
            id="string_field",
        ),
        pytest.param(
            "count",
            int,
            10,
            50,
            "The count field. The default value is `10`.",
            "The count field. The default value is `50`.",
            id="integer_field",
        ),
        pytest.param(
            "enabled",
            bool,
            False,
            True,
            "Enable this feature. The default value is `False`.",
            "Enable this feature. The default value is `True`.",
            id="boolean_field",
        ),
        pytest.param(
            "field",
            str,
            "original",
            "new_value",
            "A simple field without default mention.",
            "A simple field without default mention.",
            id="unchanged_description",
        ),
    ],
)
def test_variant_pydantic_model_updates_field_descriptions(
    field_name: str,
    field_type: type,
    old_default: Any,
    new_default: Any,
    base_description: str,
    expected_description: str,
):
    base_fields = {
        "disc": (str, pydantic.Field(default="base")),
        field_name: (
            field_type,
            pydantic.Field(default=old_default, description=base_description),
        ),
    }
    Base = pydantic.create_model("Base", **base_fields)

    # Create variant class
    VariantClass = create_variant_pydantic_model(
        variant_name="custom",
        defaults={"disc": "custom", field_name: new_default},
        base_class=Base,
        discriminator_field="disc",
        class_name_suffix="Class",
        module_name="test",
    )

    # Check description was updated correctly
    field_info = VariantClass.model_fields[field_name]
    assert field_info.description == expected_description


def test_variant_pydantic_model_updates_discriminator_description():
    class Base(pydantic.BaseModel):
        variant: str = pydantic.Field(
            default="base", description="The variant type. The default value is `base`."
        )
        value: int = 1

    VariantClass = create_variant_pydantic_model(
        variant_name="custom",
        defaults={"variant": "custom", "value": 42},
        base_class=Base,
        discriminator_field="variant",
        class_name_suffix="Class",
        module_name="test",
    )

    field_info = VariantClass.model_fields["variant"]
    assert field_info.description == "The variant type. The default value is `custom`."


def test_variant_pydantic_model_nested_field_descriptions_are_updated():
    class NestedConfig(pydantic.BaseModel):
        font_family: str = pydantic.Field(
            default="Arial",
            description="The font family. The default value is `Arial`.",
        )
        font_size: str = pydantic.Field(
            default="12pt", description="The font size. The default value is `12pt`."
        )

    class Config(pydantic.BaseModel):
        disc: str = "base"
        nested: NestedConfig = NestedConfig()

    defaults = {
        "disc": "custom",
        "nested": {
            "font_family": "Helvetica",
            "font_size": "14pt",
        },
    }

    VariantClass = create_variant_pydantic_model(
        variant_name="custom",
        defaults=defaults,
        base_class=Config,
        discriminator_field="disc",
        class_name_suffix="Variant",
        module_name="test",
    )

    # Check that the nested field descriptions are updated
    nested_annotation = VariantClass.model_fields["nested"].annotation
    assert nested_annotation is not None
    assert issubclass(nested_annotation, pydantic.BaseModel)
    nested_font_family_field = nested_annotation.model_fields["font_family"]
    nested_font_size_field = nested_annotation.model_fields["font_size"]

    assert (
        nested_font_family_field.description
        == "The font family. The default value is `Helvetica`."
    )
    assert (
        nested_font_size_field.description
        == "The font size. The default value is `14pt`."
    )

    # Also verify the actual default values are correct
    instance = VariantClass()
    assert instance.nested.font_family == "Helvetica"
    assert instance.nested.font_size == "14pt"


def test_variant_pydantic_model_deeply_nested_field_descriptions_are_updated():
    class Level3(pydantic.BaseModel):
        value: int = pydantic.Field(
            default=1, description="The value. The default value is `1`."
        )

    class Level2(pydantic.BaseModel):
        level3: Level3 = Level3()
        name: str = pydantic.Field(
            default="level2", description="The name. The default value is `level2`."
        )

    class Level1(pydantic.BaseModel):
        disc: str = "base"
        level2: Level2 = Level2()

    defaults = {
        "disc": "deep",
        "level2": {
            "name": "custom_level2",
            "level3": {"value": 999},
        },
    }

    VariantClass = create_variant_pydantic_model(
        variant_name="deep",
        defaults=defaults,
        base_class=Level1,
        discriminator_field="disc",
        class_name_suffix="Variant",
        module_name="test",
    )

    # Check Level 2 field description
    level2_annotation = VariantClass.model_fields["level2"].annotation
    assert level2_annotation is not None
    assert issubclass(level2_annotation, pydantic.BaseModel)
    level2_name_field = level2_annotation.model_fields["name"]
    assert (
        level2_name_field.description
        == "The name. The default value is `custom_level2`."
    )

    # Check Level 3 field description
    level3_annotation = level2_annotation.model_fields["level3"].annotation
    assert level3_annotation is not None
    assert issubclass(level3_annotation, pydantic.BaseModel)
    level3_value_field = level3_annotation.model_fields["value"]
    assert level3_value_field.description == "The value. The default value is `999`."

    # Verify actual default values
    instance = VariantClass()
    assert instance.level2.name == "custom_level2"
    assert instance.level2.level3.value == 999


def test_variant_pydantic_model_nested_field_partial_update_preserves_descriptions():
    class Nested(pydantic.BaseModel):
        field1: str = pydantic.Field(
            default="a", description="Field 1. The default value is `a`."
        )
        field2: str = pydantic.Field(
            default="b", description="Field 2. The default value is `b`."
        )
        field3: str = pydantic.Field(
            default="c", description="Field 3. The default value is `c`."
        )

    class Outer(pydantic.BaseModel):
        disc: str = "base"
        nested: Nested = Nested()

    defaults = {
        "disc": "partial",
        "nested": {
            "field1": "updated",
        },
    }

    VariantClass = create_variant_pydantic_model(
        variant_name="partial",
        defaults=defaults,
        base_class=Outer,
        discriminator_field="disc",
        class_name_suffix="Variant",
        module_name="test",
    )

    nested_annotation = VariantClass.model_fields["nested"].annotation
    assert nested_annotation is not None
    assert issubclass(nested_annotation, pydantic.BaseModel)

    # Updated field should have new description
    assert (
        nested_annotation.model_fields["field1"].description
        == "Field 1. The default value is `updated`."
    )

    # Non-updated fields should preserve original descriptions
    assert (
        nested_annotation.model_fields["field2"].description
        == "Field 2. The default value is `b`."
    )
    assert (
        nested_annotation.model_fields["field3"].description
        == "Field 3. The default value is `c`."
    )

    # Verify values
    instance = VariantClass()
    assert instance.nested.field1 == "updated"
    assert instance.nested.field2 == "b"
    assert instance.nested.field3 == "c"
