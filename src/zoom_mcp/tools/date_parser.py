"""
Natural Language Date/Time Parser

Convert natural language date/time expressions to ISO format for Zoom API.
"""

from datetime import datetime, timedelta
from typing import Optional
import re
from zoneinfo import ZoneInfo


def parse_natural_datetime(
    text: str,
    timezone: str = "Europe/London",
    reference_time: Optional[datetime] = None
) -> str:
    """
    Parse natural language date/time to ISO format.

    Args:
        text: Natural language datetime (e.g., "Tuesday at 3pm", "tomorrow morning")
        timezone: Timezone string (default: Europe/London)
        reference_time: Reference datetime for relative calculations

    Returns:
        ISO format datetime string (YYYY-MM-DDTHH:MM:SSZ)

    Examples:
        "Tuesday at 3pm" -> "2025-10-22T15:00:00Z"
        "tomorrow at 10am" -> "2025-10-17T10:00:00Z"
        "next Friday morning" -> "2025-10-25T09:00:00Z"
        "in 2 hours" -> "2025-10-16T05:30:00Z"
    """
    if reference_time is None:
        reference_time = datetime.now(ZoneInfo(timezone))

    text_lower = text.lower().strip()

    # Try to extract time first
    time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)', text_lower)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2)) if time_match.group(2) else 0
        period = time_match.group(3)

        if period == 'pm' and hour != 12:
            hour += 12
        elif period == 'am' and hour == 12:
            hour = 0
    else:
        # Default times based on keywords
        if 'morning' in text_lower:
            hour, minute = 9, 0
        elif 'afternoon' in text_lower:
            hour, minute = 14, 0
        elif 'evening' in text_lower:
            hour, minute = 18, 0
        elif 'night' in text_lower:
            hour, minute = 20, 0
        else:
            hour, minute = 10, 0  # Default to 10am

    # Parse date
    target_date = None

    # Relative days
    if 'today' in text_lower:
        target_date = reference_time.date()
    elif 'tomorrow' in text_lower:
        target_date = (reference_time + timedelta(days=1)).date()
    elif 'day after tomorrow' in text_lower:
        target_date = (reference_time + timedelta(days=2)).date()
    elif 'next week' in text_lower:
        target_date = (reference_time + timedelta(weeks=1)).date()

    # Specific days of week
    days_of_week = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6
    }

    for day_name, day_num in days_of_week.items():
        if day_name in text_lower:
            current_day = reference_time.weekday()
            days_ahead = day_num - current_day

            if days_ahead <= 0 or 'next' in text_lower:
                days_ahead += 7

            target_date = (reference_time + timedelta(days=days_ahead)).date()
            break

    # Relative time (in X hours/minutes)
    in_match = re.search(r'in (\d+)\s*(hour|minute|day)s?', text_lower)
    if in_match:
        amount = int(in_match.group(1))
        unit = in_match.group(2)

        if unit == 'minute':
            target_time = reference_time + timedelta(minutes=amount)
        elif unit == 'hour':
            target_time = reference_time + timedelta(hours=amount)
        elif unit == 'day':
            target_time = reference_time + timedelta(days=amount)

        return target_time.astimezone(ZoneInfo('UTC')).strftime('%Y-%m-%dT%H:%M:%SZ')

    # If no date found, default to today
    if target_date is None:
        target_date = reference_time.date()

    # Combine date and time
    target_datetime = datetime(
        target_date.year,
        target_date.month,
        target_date.day,
        hour,
        minute,
        0,
        tzinfo=ZoneInfo(timezone)
    )

    # Convert to UTC and format
    return target_datetime.astimezone(ZoneInfo('UTC')).strftime('%Y-%m-%dT%H:%M:%SZ')


def parse_duration(text: str) -> int:
    """
    Parse natural language duration to minutes.

    Args:
        text: Natural language duration (e.g., "1 hour", "30 minutes", "90 mins")

    Returns:
        Duration in minutes
    """
    text_lower = text.lower()

    # Try to extract number and unit
    match = re.search(r'(\d+(?:\.\d+)?)\s*(hour|hr|minute|min)s?', text_lower)

    if match:
        amount = float(match.group(1))
        unit = match.group(2)

        if unit in ['hour', 'hr']:
            return int(amount * 60)
        else:  # minutes
            return int(amount)

    # Default to 60 minutes
    return 60
