"""Tests for paginator helper utilities."""

from __future__ import annotations

from app.helpers.paginators import Page, SimplePaginator


def test_simple_paginator_properties() -> None:
    """SimplePaginator exposes navigation properties."""
    paginator = SimplePaginator(num_items=120, items_per_page=10, current_page=3)

    assert paginator.items_from_in_current_page == 21
    assert paginator.items_to_in_current_page == 30
    assert paginator.has_next is True
    assert paginator.next_page == 4
    assert paginator.has_previous is True
    assert paginator.previous_page == 2
    assert paginator.current_page_str == "3"


def test_simple_paginator_pages_include_gaps() -> None:
    """SimplePaginator inserts gap markers when needed."""
    paginator = SimplePaginator(num_items=200, items_per_page=10, current_page=5)

    pages = paginator.pages

    assert any(page.page is None for page in pages)
    assert pages[0].value == "1"
    assert str(Page()) == "..."


def test_page_is_page_flags() -> None:
    """Page is_page flag reflects availability."""
    assert Page(2).is_page is True
    assert Page().is_page is False


def test_simple_paginator_single_page_properties() -> None:
    """SimplePaginator handles single-page collections."""
    paginator = SimplePaginator(num_items=5, items_per_page=10, current_page=1)

    assert paginator.has_next is False
    assert paginator.next_page is None
    assert paginator.has_previous is False
    assert paginator.previous_page is None
    assert paginator.items_to_in_current_page == 5
