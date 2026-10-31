# Add a New Social Network

A user writes a network and a username, and RenderCV turns them into a link to that profile, shown with the network's icon. Two parts of RenderCV are involved. The schema checks the username and builds the profile's web address. The renderer adds the icon in PDFs, or the network's name in Markdown. Adding a network means teaching both parts about it.

1. Add the network's name to `SocialNetworkName` in `src/rendercv/schema/models/cv/social_network.py`. This list is what the input is checked against, so only names in it are accepted:

    ```python
    type SocialNetworkName = Literal[
        "LinkedIn",
        "GitHub",
        # ... existing networks
        "MyNetwork",
    ]
    ```

2. Add the start of its profile addresses to `url_dictionary` in the same file. RenderCV appends the username to it:

    ```python
    url_dictionary: dict[SocialNetworkName, str] = {
        "LinkedIn": "https://linkedin.com/in/",
        # ... existing networks
        "MyNetwork": "https://mynetwork.com/profile/",
    }
    ```

3. If the network's usernames follow rules, check them in `check_username`, in the same file. A wrong username is then reported when the CV is checked, instead of producing a broken link:

    ```python
    match network:
        case "Mastodon":
            # ... existing checks
        case "MyNetwork":
            # ... your checks
    ```

4. If the address isn't simply the start plus the username, build it in the `url` property, in the same file. Mastodon, for example, turns `@user@domain` into `https://domain/@user`:

    ```python
    @functools.cached_property
    def url(self) -> str:
        if self.network == "Mastodon":
            # ... existing special cases
        elif self.network == "MyNetwork":
            # ... your address
        else:
            url = url_dictionary[self.network] + self.username
        return url
    ```

    Confirm the address format and username rules with the platform's own documentation or sign-up form, and don't confuse a profile's address name with its display name. Itch.io, for example, puts the username in the domain (`https://username.itch.io/`), while HuggingFace and Devpost put it in the path. WhatsApp links usernames as `https://wa.me/username` and international phone numbers, digits only, as `https://wa.me/14155552671` ([username links](https://faq.whatsapp.com/1561101675623754/), [username rules](https://faq.whatsapp.com/2535820043482794/)).

5. Choose its icon in `fontawesome_icons` in `src/rendercv/renderer/templater/connections.py`:

    ```python
    fontawesome_icons = {
        "LinkedIn": "linkedin",
        # ... existing icons
        "MyNetwork": "my-icon-name",
    }
    ```

    The icons come from [Font Awesome](https://fontawesome.com/search), a collection of icons stored as a font: each icon is a character, so it scales and prints as sharply as text. Two pieces must know the icon: the Font Awesome Typst package, whose version `src/rendercv/renderer/rendercv_typst/lib.typ` imports, maps the name to its character, and the Font Awesome fonts in `packages/rendercv-fonts` draw it. `test_every_icon_has_a_glyph` checks both.

6. Test the address in `tests/schema/models/cv/test_social_network.py`:

    ```python
    @pytest.mark.parametrize(
        ("network", "username", "expected_url"),
        [
            # ... existing cases
            (
                "MyNetwork",
                "myusername",
                "https://mynetwork.com/profile/myusername",
            ),
        ],
    )
    def test_url(self, network, username, expected_url):
        # existing test body
    ```

7. Add the network to the sample CV the renderer tests use, the `social_networks` list in `tests/renderer/conftest.py`:

    ```python
    social_networks=[
        SocialNetwork(network="LinkedIn", username="johndoe"),
        # ... existing networks
        SocialNetwork(network="MyNetwork", username="johndoe"),
    ]
    ```

8. Regenerate the schema, which lists every network. Then update the reference files, check in the PDFs in `tests/renderer/testdata/test_pdf_png/` that the icon and link look right, and run the tests:

    ```bash
    just update-schema
    just update-testdata
    just test
    ```
