"""Tests for calculator_tool."""
from __future__ import annotations

import pytest
from harness.tools.calculator_tool import calculator_tool, SAFE_MATH


@pytest.mark.asyncio
async def test_basic_arithmetic():
    result = await calculator_tool("2 + 3")
    assert result == "5"

    result = await calculator_tool("10 - 4")
    assert result == "6"

    result = await calculator_tool("3 * 7")
    assert result == "21"

    result = await calculator_tool("15 / 3")
    assert result == "5.0"


@pytest.mark.asyncio
async def test_safe_math_functions():
    result = await calculator_tool("sqrt(16)")
    assert result == "4.0"

    result = await calculator_tool("abs(-5)")
    assert result == "5"

    result = await calculator_tool("pow(2, 3)")
    assert result == "8"

    result = await calculator_tool("round(3.7)")
    assert result == "4"

    result = await calculator_tool("floor(3.9)")
    assert result == "3"

    result = await calculator_tool("ceil(3.1)")
    assert result == "4"


@pytest.mark.asyncio
async def test_log_and_trig():
    result = await calculator_tool("log(e)")
    assert result == "1.0"

    result = await calculator_tool("sin(0)")
    assert result == "0.0"

    result = await calculator_tool("cos(0)")
    assert result == "1.0"


@pytest.mark.asyncio
async def test_division_by_zero():
    result = await calculator_tool("1 / 0")
    assert result.startswith("Error:")


@pytest.mark.asyncio
async def test_invalid_expression():
    result = await calculator_tool("open('/etc/passwd')")
    assert result.startswith("Error:")


@pytest.mark.asyncio
async def test_malformed_expression():
    result = await calculator_tool("1 +")
    assert result.startswith("Error:")


@pytest.mark.asyncio
async def test_constants():
    result = await calculator_tool("pi")
    assert result == str(SAFE_MATH["pi"])

    result = await calculator_tool("e")
    assert result == str(SAFE_MATH["e"])


@pytest.mark.asyncio
async def test_complex_expression():
    result = await calculator_tool("sqrt(9) + pow(2, 3)")
    assert result == "11.0"