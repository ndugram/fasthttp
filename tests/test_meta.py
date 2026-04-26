"""Tests for __meta__.py version string."""
import fasthttp.__meta__ as meta


class TestMeta:
    def test_version_exists(self):
        assert hasattr(meta, "__version__")

    def test_version_is_string(self):
        assert isinstance(meta.__version__, str)

    def test_version_not_empty(self):
        assert meta.__version__ != ""

    def test_version_semver_format(self):
        parts = meta.__version__.split(".")
        assert len(parts) >= 2
        for part in parts:
            assert part.isdigit(), f"Non-numeric part: {part!r}"

    def test_version_importable_from_fasthttp(self):
        import fasthttp
        assert hasattr(fasthttp, "__version__")
        assert fasthttp.__version__ == meta.__version__
