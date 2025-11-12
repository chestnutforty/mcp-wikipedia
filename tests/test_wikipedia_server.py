import pytest
from wikipedia_server import search_wikipedia


@pytest.mark.asyncio
async def test_search_basic():
    """Test basic Wikipedia search"""
    result = await search_wikipedia.fn(
        query="Python programming language",
        end_date="2024-01-01"
    )

    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0
    # Should contain article markers
    assert "===" in result


@pytest.mark.asyncio
async def test_search_with_historical_date():
    """Test search with older historical date"""
    result = await search_wikipedia.fn(
        query="World War II",
        end_date="2020-01-01",
        limit=1
    )

    assert result is not None
    assert "World War" in result or "===" in result
    assert "2020-01-01" in result or "before" in result.lower()


@pytest.mark.asyncio
async def test_search_multiple_articles():
    """Test searching for multiple articles"""
    result = await search_wikipedia.fn(
        query="Albert Einstein",
        end_date="2023-06-01",
        limit=3
    )

    assert result is not None
    assert "===" in result
    # With limit=3, we might get multiple articles
    assert len(result) > 100  # Should have substantial content


@pytest.mark.asyncio
async def test_search_with_different_language():
    """Test search with non-English language"""
    result = await search_wikipedia.fn(
        query="Paris",
        end_date="2023-01-01",
        lang="fr",
        limit=1
    )

    assert result is not None
    assert isinstance(result, str)
    # Either returns French content or an error message
    assert len(result) > 0


@pytest.mark.asyncio
async def test_search_no_results():
    """Test search that returns no results"""
    result = await search_wikipedia.fn(
        query="xyzabcnotarealwikipediaarticle123456",
        end_date="2024-01-01",
        limit=2
    )

    assert result is not None
    # Should indicate no results found
    assert "no" in result.lower() or "not found" in result.lower()

