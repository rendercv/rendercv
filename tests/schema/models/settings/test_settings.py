from rendercv.schema.models.settings.settings import Settings


class TestKeepUniqueKeywords:
    def test_removes_duplicates(self):
        settings = Settings(bold_keywords=["Python", "Java", "Python", "C++", "Java"])

        assert len(settings.bold_keywords) == 3
        assert set(settings.bold_keywords) == {"Python", "Java", "C++"}

    def test_with_empty_list(self):
        settings = Settings(bold_keywords=[])

        assert settings.bold_keywords == []

    def test_with_unique_list(self):
        settings = Settings(bold_keywords=["Python", "Java", "C++"])

        assert len(settings.bold_keywords) == 3
        assert set(settings.bold_keywords) == {"Python", "Java", "C++"}
