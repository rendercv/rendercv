# Add a New Social Network

1. Add network name to `SocialNetworkName` type

    Edit `src/rendercv/schema/models/cv/social_network.py`:

    ```python
    type SocialNetworkName = Literal[
        "LinkedIn",
        "GitHub",
        # ... existing networks
        "MyNetwork",  # Add your network here
    ]
    ```

2. Add URL pattern to `url_dictionary`

    Edit `src/rendercv/schema/models/cv/social_network.py`:

    ```python
    url_dictionary: dict[SocialNetworkName, str] = {
        "LinkedIn": "https://linkedin.com/in/",
        # ... existing networks
        "MyNetwork": "https://mynetwork.com/profile/",  # Add URL base here
    }
    ```

3. (Optional) Add username validation

    If your network has special username format requirements, edit `src/rendercv/schema/models/cv/social_network.py`:

    ```python
    match network:
        case "Mastodon":
            # ... existing validations
        case "MyNetwork":
            # ... your custom validation logic
    ```

4. (Optional) Add custom URL generation

    If URL generation requires special logic (not just base + username), edit `src/rendercv/schema/models/cv/social_network.py`:

    ```python
    @functools.cached_property
    def url(self) -> str:
        if self.network == "Mastodon":
            # ... existing custom logic
        elif self.network == "MyNetwork":
            # ... your custom URL generation logic
        else:
            url = url_dictionary[self.network] + self.username
        return url
    ```

5. Add Font Awesome icon

    Edit `src/rendercv/renderer/templater/connections.py`:

    ```python
    typst_fa_icons = {
        "LinkedIn": "linkedin",
        # ... existing icons
        "MyNetwork": "my-icon-name",  # Add your icon name here
    }
    ```

    See available icons at: [fontawesome.com/search](https://fontawesome.com/search)

6. Add test for URL generation

    Edit `tests/schema/models/cv/test_social_network.py`:

    ```python
    @pytest.mark.parametrize(
        ("network", "username", "expected_url"),
        [
            # ... existing tests
            (
                "MyNetwork",
                "myusername",
                "https://mynetwork.com/profile/myusername",
            ),
        ],
    )
    def test_url(self, network, username, expected_url):
        # test implementation
    ```

7. Add network to test fixtures

    Edit `tests/renderer/conftest.py`, add your network to the `social_networks` list:

    ```python
    social_networks=[
        SocialNetwork(network="LinkedIn", username="johndoe"),
        # ... existing networks
        SocialNetwork(network="MyNetwork", username="johndoe"),
    ]
    ```

8. Run tests

    ```bash
    pytest tests/schema/models/cv/test_social_network.py -v
    pytest tests/renderer/ --update-testdata  # Update reference files and check if they look good
    pytest tests/  # Verify all tests pass
    ```
