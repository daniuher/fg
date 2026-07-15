import hashlib
from pathlib import Path

import pytest
from fg.core.hashing import compute_hash, get_metadata


# ── Fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture
def sample_file(tmp_path) -> Path:
    p = tmp_path / "sample.txt"
    p.write_text("Hello from fg test.\n")
    return p


@pytest.fixture
def empty_file(tmp_path) -> Path:
    p = tmp_path / "empty.txt"
    p.touch()
    return p


# ── compute_hash tests ───────────────────────────────────────────────────

def test_compute_hash_matches_known_sha256(sample_file):
    """Sanity check: our chunked implementation must match hashlib's direct result."""
    expected = hashlib.sha256(sample_file.read_bytes()).hexdigest()
    assert compute_hash(sample_file) == expected


def test_compute_hash_is_deterministic(sample_file):
    """Hashing the same file twice must always yield the same result."""
    h1 = compute_hash(sample_file)
    h2 = compute_hash(sample_file)
    assert h1 == h2


def test_compute_hash_differs_for_different_content(tmp_path):
    """Two files with different content must never collide."""
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("content A")
    f2.write_text("content B")
    assert compute_hash(f1) != compute_hash(f2)


def test_compute_hash_same_content_different_names(tmp_path):
    """Identical content should hash identically regardless of filename/path."""
    f1 = tmp_path / "original.txt"
    f2 = tmp_path / "copy.txt"
    f1.write_text("identical payload")
    f2.write_text("identical payload")
    assert compute_hash(f1) == compute_hash(f2)


def test_compute_hash_empty_file(empty_file):
    """
    Empty files must hash to the well-known SHA-256 of zero bytes.
    This confirms the chunked read loop degrades correctly (never executes,
    hexdigest() still returns a valid hash of the empty byte string).
    """
    known_empty_sha256 = hashlib.sha256(b"").hexdigest()
    assert compute_hash(empty_file) == known_empty_sha256


def test_compute_hash_large_file_chunking(tmp_path):
    """Force multiple chunk reads to verify the loop handles chunk boundaries correctly."""
    f = tmp_path / "large.bin"
    payload = b"x" * (65536 * 3 + 17)  # 3 full chunks + a partial chunk
    f.write_bytes(payload)

    expected = hashlib.sha256(payload).hexdigest()
    assert compute_hash(f) == expected


# ── get_metadata tests ───────────────────────────────────────────────────

def test_get_metadata_fields_present(sample_file):
    meta = get_metadata(sample_file)
    expected_keys = {
        "hash", "path", "filename", "extension",
        "size_bytes", "modified_at", "registered_at",
    }
    assert expected_keys.issubset(meta.keys())


def test_get_metadata_hash_matches_compute_hash(sample_file):
    meta = get_metadata(sample_file)
    assert meta["hash"] == compute_hash(sample_file)


def test_get_metadata_size_bytes_correct(sample_file):
    meta = get_metadata(sample_file)
    assert meta["size_bytes"] == sample_file.stat().st_size


def test_get_metadata_extension_lowercased(tmp_path):
    f = tmp_path / "scan.NII.GZ"
    f.write_text("dummy")
    meta = get_metadata(f)
    assert meta["extension"] == ".gz"  # Path.suffix only grabs the last suffix


def test_get_metadata_no_extension(tmp_path):
    f = tmp_path / "README"
    f.write_text("no extension")
    meta = get_metadata(f)
    assert meta["extension"] is None


def test_get_metadata_raises_on_missing_file(tmp_path):
    missing = tmp_path / "does_not_exist.txt"
    with pytest.raises(FileNotFoundError):
        get_metadata(missing)


def test_get_metadata_path_is_absolute(sample_file):
    meta = get_metadata(sample_file)
    assert Path(meta["path"]).is_absolute()
