from rendercv.schema.models.settings.settings import Settings


def test_keep_unique_keywords_removes_duplicates():
    settings = Settings(bold_keywords=["Python", "Java", "Python", "C++", "Java"])

    # Should only contain unique keywords
    assert len(settings.bold_keywords) == 3
    assert set(settings.bold_keywords) == {"Python", "Java", "C++"}


def test_keep_unique_keywords_with_empty_list():
    settings = Settings(bold_keywords=[])

    assert settings.bold_keywords == []


def test_keep_unique_keywords_with_unique_list():
    settings = Settings(bold_keywords=["Python", "Java", "C++"])

    assert len(settings.bold_keywords) == 3
    assert set(settings.bold_keywords) == {"Python", "Java", "C++"}
