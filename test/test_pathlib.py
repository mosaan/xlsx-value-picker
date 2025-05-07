from pathlib import Path


def test_relative():
    # Test relative path
    relative_path = Path("test/test_config.yaml")
    assert relative_path.is_file(), f"Expected {relative_path} to be a file."

    # Test absolute path
    absolute_path = Path(__file__).resolve().parent / "test_config.yaml"
    assert absolute_path.is_file(), f"Expected {absolute_path} to be a file."

    # Test parent directory
    parent_dir = Path(__file__).resolve().parent
    assert parent_dir.is_dir(), f"Expected {parent_dir} to be a directory."
