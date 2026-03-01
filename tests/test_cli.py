import pytest
from profiles import ALL_PROFILES
from cli import _resolve_profile, _validate_name


class TestProfileSlugs:
    def test_all_profiles_have_slug(self):
        for p in ALL_PROFILES:
            assert hasattr(p, "slug"), f"{p.__class__.__name__} is missing 'slug'"
            assert p.slug, f"{p.__class__.__name__}.slug must be non-empty"

    def test_slugs_are_unique(self):
        slugs = [p.slug for p in ALL_PROFILES]
        assert len(slugs) == len(set(slugs)), f"Duplicate slugs: {slugs}"

    def test_slugs_are_lowercase_alphanumeric(self):
        for p in ALL_PROFILES:
            assert p.slug == p.slug.lower(), (
                f"{p.__class__.__name__}.slug must be lowercase"
            )
            assert p.slug.replace("-", "").isalnum(), (
                f"{p.__class__.__name__}.slug has invalid chars"
            )


class TestResolveProfile:
    def test_valid_slug_returns_correct_index(self):
        for i, p in enumerate(ALL_PROFILES):
            assert _resolve_profile(p.slug) == i

    def test_slug_case_insensitive(self):
        first_slug = ALL_PROFILES[0].slug
        assert _resolve_profile(first_slug.upper()) == 0

    def test_valid_number_string_returns_zero_based_index(self):
        assert _resolve_profile("1") == 0
        assert _resolve_profile(str(len(ALL_PROFILES))) == len(ALL_PROFILES) - 1

    def test_number_out_of_range_returns_none(self):
        assert _resolve_profile("0") is None
        assert _resolve_profile(str(len(ALL_PROFILES) + 1)) is None

    def test_unknown_slug_returns_none(self):
        assert _resolve_profile("does-not-exist") is None
        assert _resolve_profile("") is None


class TestValidateName:
    @pytest.mark.parametrize("name", ["my-project", "my_project", "MyProject123", "a"])
    def test_valid_names(self, name):
        assert _validate_name(name) is None

    @pytest.mark.parametrize(
        "name", ["", "my/project", "my:project", "../evil", "my..project"]
    )
    def test_invalid_names_return_message(self, name):
        assert _validate_name(name) is not None
