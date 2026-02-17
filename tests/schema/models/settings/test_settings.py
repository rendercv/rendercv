from rendercv.schema.models.settings.settings import Settings


class TestSettings:
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

    def test_pdf_title_default(self):
        settings = Settings()

        assert settings.pdf_title == "NAME - CV"

    def test_pdf_title_custom(self):
        settings = Settings(pdf_title="NAME - Resume YEAR")

        assert settings.pdf_title == "NAME - Resume YEAR"
