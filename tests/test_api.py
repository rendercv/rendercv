import rendercv


def test_rendercv():
    assert isinstance(
        rendercv.create_contents_of_a_typst_file({"cv": {"name": "John Doe"}}), str
    )
