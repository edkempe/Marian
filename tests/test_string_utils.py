"""Tests for string utilities."""

import pytest
from utils.string_utils import (
    camel_to_snake,
    snake_to_camel,
    split_keep_delimiters
)

def test_camel_to_snake():
    """Test camelCase to snake_case conversion."""
    assert camel_to_snake("camelCase") == "camel_case"
    assert camel_to_snake("ThisIsATest") == "this_is_a_test"
    assert camel_to_snake("ABC") == "a_b_c"
    assert camel_to_snake("already_snake") == "already_snake"

def test_snake_to_camel():
    """Test snake_case to camelCase conversion."""
    assert snake_to_camel("snake_case") == "SnakeCase"
    assert snake_to_camel("this_is_a_test") == "ThisIsATest"
    assert snake_to_camel("a_b_c") == "ABC"
    assert snake_to_camel("AlreadyCamel") == "AlreadyCamel"

def test_split_keep_delimiters():
    """Test splitting text while keeping delimiters."""
    text = "Hello, World! How are you?"
    delimiters = ",.!?"
    expected = ["Hello", ",", " World", "!", " How are you", "?"]
    assert split_keep_delimiters(text, delimiters) == expected

    # Test with no delimiters in text
    text = "Hello World"
    assert split_keep_delimiters(text, delimiters) == ["Hello World"]

    # Test with empty text
    assert split_keep_delimiters("", delimiters) == []
