import os

from app.services.evidence.pipeline import is_path_contained, safe_filename


def test_safe_filename_strips_unix_traversal():
    result = safe_filename("../../../../etc/cron.d/evil")
    assert ".." not in result
    assert "/" not in result
    assert result == "evil"


def test_safe_filename_strips_windows_style_traversal():
    result = safe_filename("..\\..\\..\\evil.txt")
    assert ".." not in result
    assert "\\" not in result
    assert "/" not in result
    assert result == "evil.txt"


def test_safe_filename_strips_absolute_unix_path():
    result = safe_filename("/etc/passwd")
    assert "/" not in result
    assert result == "passwd"


def test_safe_filename_strips_absolute_windows_path():
    result = safe_filename("C:\\Windows\\System32\\evil.dll")
    assert "\\" not in result
    assert "/" not in result
    assert result == "evil.dll"


def test_safe_filename_handles_null_byte_trick():
    result = safe_filename("evil.txt\x00.png")
    assert "\x00" not in result
    assert result == "evil.txt"


def test_safe_filename_handles_pure_traversal_with_no_basename():
    # ".." alone, or a string that is only separators/dots, must not survive
    # as something that could reassemble into a traversal sequence.
    for bad in ["..", "../..", "....//....//", "\\\\..\\\\.."]:
        result = safe_filename(bad)
        assert ".." not in result
        assert result != ""


def test_safe_filename_empty_or_none_falls_back():
    assert safe_filename(None) == "upload"
    assert safe_filename("") == "upload"


def test_safe_filename_preserves_normal_filenames():
    assert safe_filename("whatsapp_export.txt") == "whatsapp_export.txt"
    assert safe_filename("Bank Statement (June 2026).pdf") == "Bank Statement (June 2026).pdf"


def test_safe_filename_strips_unsafe_special_characters():
    result = safe_filename("evil<script>.txt")
    assert "<" not in result and ">" not in result


def test_is_path_contained_true_for_direct_child(tmp_path):
    base = str(tmp_path)
    candidate = os.path.join(base, "file.txt")
    assert is_path_contained(base, candidate)


def test_is_path_contained_false_for_traversal_outside_base(tmp_path):
    base = os.path.join(str(tmp_path), "storage")
    os.makedirs(base)
    candidate = os.path.join(base, "..", "..", "escaped.txt")
    assert not is_path_contained(base, candidate)


def test_is_path_contained_false_for_sibling_directory(tmp_path):
    base = os.path.join(str(tmp_path), "storage")
    sibling = os.path.join(str(tmp_path), "storage_evil")
    os.makedirs(base)
    os.makedirs(sibling)
    candidate = os.path.join(sibling, "file.txt")
    assert not is_path_contained(base, candidate)
