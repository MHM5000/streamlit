# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022-2026)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""quick_select_options unit tests for date_input."""

from datetime import date, datetime, timedelta

import pytest

import streamlit as st
from streamlit.errors import StreamlitAPIException
from tests.delta_generator_test_case import DeltaGeneratorTestCase


class QuickSelectOptionsTest(DeltaGeneratorTestCase):
    """Test quick_select_options parameter for date_input."""

    def test_quick_select_with_relative_dates(self):
        """Test quick_select_options with timedelta values."""
        st.date_input(
            "Select range",
            value=[],
            quick_select_options={
                "Last Week": (timedelta(days=-7), timedelta(days=0)),
                "Last Month": (timedelta(days=-30), "today"),
            },
        )

        c = self.get_delta_from_queue().new_element.date_input
        assert len(c.quick_select_options) == 2

        # Check first option
        assert c.quick_select_options[0].id == "Last Week"
        assert c.quick_select_options[0].begin_date  # Should be a valid ISO date
        assert c.quick_select_options[0].end_date

        # Check second option
        assert c.quick_select_options[1].id == "Last Month"

    def test_quick_select_with_absolute_dates(self):
        """Test quick_select_options with absolute date values."""
        st.date_input(
            "Select quarter",
            value=[],
            quick_select_options={
                "Q1 2025": (date(2025, 1, 1), date(2025, 3, 31)),
                "Q2 2025": (date(2025, 4, 1), date(2025, 6, 30)),
            },
        )

        c = self.get_delta_from_queue().new_element.date_input
        assert len(c.quick_select_options) == 2
        assert c.quick_select_options[0].id == "Q1 2025"
        assert c.quick_select_options[0].begin_date == "2025/01/01"
        assert c.quick_select_options[0].end_date == "2025/03/31"

    def test_quick_select_with_datetime_objects(self):
        """Test quick_select_options with datetime objects."""
        st.date_input(
            "Select range",
            value=[],
            quick_select_options={
                "Custom": (datetime(2025, 1, 1, 10, 30), datetime(2025, 1, 31, 15, 45)),
            },
        )

        c = self.get_delta_from_queue().new_element.date_input
        assert len(c.quick_select_options) == 1
        # Time should be stripped, only date remains
        assert c.quick_select_options[0].begin_date == "2025/01/01"
        assert c.quick_select_options[0].end_date == "2025/01/31"

    def test_quick_select_with_iso_strings(self):
        """Test quick_select_options with ISO date strings."""
        st.date_input(
            "Select range",
            value=[],
            quick_select_options={
                "Custom": ("2025-01-01", "2025-12-31"),
            },
        )

        c = self.get_delta_from_queue().new_element.date_input
        assert len(c.quick_select_options) == 1
        assert c.quick_select_options[0].begin_date == "2025/01/01"
        assert c.quick_select_options[0].end_date == "2025/12/31"

    def test_quick_select_with_today_literal(self):
        """Test quick_select_options with 'today' literal."""
        st.date_input(
            "Select range",
            value=[],
            quick_select_options={
                "Until Today": (date(2025, 1, 1), "today"),
                "From Today": ("today", date(2025, 12, 31)),
            },
        )

        c = self.get_delta_from_queue().new_element.date_input
        assert len(c.quick_select_options) == 2
        # Today should be resolved to an actual date
        assert c.quick_select_options[0].begin_date == "2025/01/01"
        assert c.quick_select_options[0].end_date  # Should be today's date
        assert c.quick_select_options[1].end_date == "2025/12/31"

    def test_quick_select_with_mixed_types(self):
        """Test quick_select_options with mixed date types."""
        st.date_input(
            "Select range",
            value=[],
            quick_select_options={
                "Option 1": (timedelta(days=-7), "today"),
                "Option 2": (date(2025, 1, 1), date(2025, 3, 31)),
                "Option 3": ("2025-04-01", datetime(2025, 6, 30, 23, 59)),
            },
        )

        c = self.get_delta_from_queue().new_element.date_input
        assert len(c.quick_select_options) == 3

    def test_quick_select_empty_dict_disables_quick_select(self):
        """Test that empty dict explicitly disables quick select."""
        st.date_input(
            "Select range",
            value=[],
            min_value=date(2020, 1, 1),  # Old enough to normally trigger quick select
            quick_select_options={},
        )

        c = self.get_delta_from_queue().new_element.date_input
        assert len(c.quick_select_options) == 0

    def test_quick_select_none_uses_default_behavior(self):
        """Test that None uses default auto-enable behavior."""
        st.date_input(
            "Select range",
            value=[],
            min_value=date(2020, 1, 1),
            quick_select_options=None,
        )

        c = self.get_delta_from_queue().new_element.date_input
        # Should not have custom options (None means use default behavior)
        assert len(c.quick_select_options) == 0

    def test_quick_select_fails_with_single_date(self):
        """Test that quick_select_options raises error for single date input."""
        with pytest.raises(StreamlitAPIException) as e:
            st.date_input(
                "Select date",
                value=date.today(),  # Single date, not a range
                quick_select_options={
                    "Last Week": (timedelta(days=-7), timedelta(days=0)),
                },
            )

        assert "quick_select_options can only be used with date range inputs" in str(
            e.value
        )

    def test_quick_select_fails_with_non_dict(self):
        """Test that quick_select_options raises error for non-dict."""
        with pytest.raises(StreamlitAPIException) as e:
            st.date_input(
                "Select range",
                value=[],
                quick_select_options="invalid",  # type: ignore
            )

        assert "must be a dict" in str(e.value)

    def test_quick_select_with_invalid_date_string(self):
        """Test that invalid date strings raise appropriate errors."""
        with pytest.raises(StreamlitAPIException) as e:
            st.date_input(
                "Select range",
                value=[],
                quick_select_options={
                    "Invalid": ("not-a-date", "2025-01-01"),
                },
            )

        assert "Invalid date string" in str(e.value)

    def test_quick_select_preserves_order(self):
        """Test that quick_select_options preserves insertion order."""
        st.date_input(
            "Select range",
            value=[],
            quick_select_options={
                "Third": (date(2025, 7, 1), date(2025, 9, 30)),
                "First": (date(2025, 1, 1), date(2025, 3, 31)),
                "Second": (date(2025, 4, 1), date(2025, 6, 30)),
            },
        )

        c = self.get_delta_from_queue().new_element.date_input
        # Dictionary order should be preserved (Python 3.7+)
        assert c.quick_select_options[0].id == "Third"
        assert c.quick_select_options[1].id == "First"
        assert c.quick_select_options[2].id == "Second"
