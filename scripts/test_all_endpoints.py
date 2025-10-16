#!/usr/bin/env python3
"""
Comprehensive Zoom MCP API Testing Script

Tests all REST API endpoints and reports results with ✓ or ✗
"""

import httpx
import asyncio
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import sys

BASE_URL = "http://zoom-mcp.theaiconsultant.co.uk:3001"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class TestResult:
    def __init__(self, endpoint: str, method: str):
        self.endpoint = endpoint
        self.method = method
        self.passed = False
        self.error = None
        self.response_data = None
        self.status_code = None

    def __str__(self):
        status = f"{Colors.GREEN}✓{Colors.RESET}" if self.passed else f"{Colors.RED}✗{Colors.RESET}"
        result = f"{status} {Colors.BOLD}{self.method}{Colors.RESET} {self.endpoint}"

        if self.status_code:
            result += f" ({self.status_code})"

        if not self.passed and self.error:
            result += f"\n  {Colors.RED}Error: {self.error}{Colors.RESET}"

        return result


async def test_endpoint(
    client: httpx.AsyncClient,
    method: str,
    endpoint: str,
    **kwargs
) -> TestResult:
    """Test a single endpoint and return result."""
    result = TestResult(endpoint, method)

    try:
        if method == "GET":
            response = await client.get(f"{BASE_URL}{endpoint}", **kwargs)
        elif method == "POST":
            response = await client.post(f"{BASE_URL}{endpoint}", **kwargs)
        elif method == "PATCH":
            response = await client.patch(f"{BASE_URL}{endpoint}", **kwargs)
        elif method == "DELETE":
            response = await client.delete(f"{BASE_URL}{endpoint}", **kwargs)

        result.status_code = response.status_code

        # Consider 2xx and 404 (for searches with no results) as success
        if 200 <= response.status_code < 300:
            result.passed = True
            result.response_data = response.json() if response.content else None
        elif response.status_code == 404 and "find" in endpoint:
            # 404 is expected for searches with no matches
            result.passed = True
            result.error = "No matching results (expected)"
        else:
            result.error = f"HTTP {response.status_code}: {response.text[:200]}"

    except Exception as e:
        result.error = str(e)

    return result


async def run_all_tests() -> Tuple[List[TestResult], int, int]:
    """Run all endpoint tests."""
    results = []

    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}Zoom MCP API Comprehensive Test Suite{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")
    print(f"Testing against: {Colors.YELLOW}{BASE_URL}{Colors.RESET}\n")

    async with httpx.AsyncClient(timeout=30.0) as client:

        # Test 1: Root endpoint
        print(f"{Colors.BOLD}1. Core Endpoints{Colors.RESET}")
        result = await test_endpoint(client, "GET", "/")
        results.append(result)
        print(f"  {result}")

        result = await test_endpoint(client, "GET", "/api")
        results.append(result)
        print(f"  {result}")

        # Test 2: User endpoints
        print(f"\n{Colors.BOLD}2. User Management{Colors.RESET}")
        result = await test_endpoint(client, "GET", "/api/users")
        results.append(result)
        print(f"  {result}")

        result = await test_endpoint(client, "GET", "/api/users/me")
        results.append(result)
        print(f"  {result}")

        # Test 3: Meeting listing
        print(f"\n{Colors.BOLD}3. Meeting Listing{Colors.RESET}")
        result = await test_endpoint(client, "GET", "/api/meetings")
        results.append(result)
        print(f"  {result}")

        result = await test_endpoint(client, "GET", "/api/meetings/today")
        results.append(result)
        print(f"  {result}")

        result = await test_endpoint(client, "GET", "/api/meetings/upcoming")
        results.append(result)
        print(f"  {result}")

        # Test 4: Create meeting
        print(f"\n{Colors.BOLD}4. Meeting Creation{Colors.RESET}")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT10:00:00Z")

        meeting_data = {
            "topic": "Test Meeting - Automated Test",
            "type": 2,
            "start_time": tomorrow,
            "duration": 30,
            "timezone": "Europe/London",
            "agenda": "Automated testing of Zoom MCP API"
        }

        result = await test_endpoint(
            client, "POST", "/api/meetings",
            json=meeting_data
        )
        results.append(result)
        print(f"  {result}")

        created_meeting_id = None
        if result.passed and result.response_data:
            created_meeting_id = result.response_data.get("id")
            print(f"  {Colors.GREEN}Created meeting ID: {created_meeting_id}{Colors.RESET}")

        # Test 5: Natural language booking
        print(f"\n{Colors.BOLD}5. Natural Language Booking{Colors.RESET}")
        nl_booking_data = {
            "when": "tomorrow at 3pm",
            "topic": "Test NL Meeting",
            "duration": "1 hour",
            "timezone": "Europe/London"
        }

        result = await test_endpoint(
            client, "POST", "/api/meetings/book-natural",
            json=nl_booking_data
        )
        results.append(result)
        print(f"  {result}")

        nl_meeting_id = None
        if result.passed and result.response_data:
            nl_meeting_id = result.response_data.get("id")
            print(f"  {Colors.GREEN}Created NL meeting ID: {nl_meeting_id}{Colors.RESET}")

        # Test 6: Meeting search
        print(f"\n{Colors.BOLD}6. Meeting Search{Colors.RESET}")
        result = await test_endpoint(client, "GET", "/api/meetings/find/Test")
        results.append(result)
        print(f"  {result}")

        result = await test_endpoint(client, "GET", "/api/meetings/find/NonExistentMeeting12345")
        results.append(result)
        print(f"  {result}")

        # Test 7: Contact search
        print(f"\n{Colors.BOLD}7. Contact Management{Colors.RESET}")
        result = await test_endpoint(client, "GET", "/api/contacts/search/Agostino")
        results.append(result)
        print(f"  {result}")

        result = await test_endpoint(client, "GET", "/api/contacts/search/Paul")
        results.append(result)
        print(f"  {result}")

        # Test 8: Book with contact
        print(f"\n{Colors.BOLD}8. Book Meeting with Contact{Colors.RESET}")
        contact_booking_data = {
            "contact_name": "Agostino",
            "when": "Friday at 1:30pm",
            "duration": "45 minutes",
            "topic": "Test Contact Meeting"
        }

        result = await test_endpoint(
            client, "POST", "/api/meetings/book-with-contact",
            json=contact_booking_data
        )
        results.append(result)
        print(f"  {result}")

        # Test 9: Meeting management (if we have a meeting)
        test_meeting_id = created_meeting_id or nl_meeting_id

        if test_meeting_id:
            print(f"\n{Colors.BOLD}9. Meeting Management (ID: {test_meeting_id}){Colors.RESET}")

            # Get specific meeting
            result = await test_endpoint(client, "GET", f"/api/meetings/{test_meeting_id}")
            results.append(result)
            print(f"  {result}")

            # Update meeting
            update_data = {
                "topic": "Updated Test Meeting",
                "agenda": "Updated agenda via API"
            }
            result = await test_endpoint(
                client, "PATCH", f"/api/meetings/{test_meeting_id}",
                json=update_data
            )
            results.append(result)
            print(f"  {result}")

            # Delete meeting
            result = await test_endpoint(client, "DELETE", f"/api/meetings/{test_meeting_id}")
            results.append(result)
            print(f"  {result}")
        else:
            print(f"\n{Colors.BOLD}9. Meeting Management{Colors.RESET}")
            print(f"  {Colors.YELLOW}⚠ Skipped - No meeting ID available{Colors.RESET}")

        # Test 10: Post-meeting automation (with a realistic meeting ID)
        print(f"\n{Colors.BOLD}10. Post-Meeting Automation{Colors.RESET}")
        print(f"  {Colors.YELLOW}Note: These require a completed meeting with recordings{Colors.RESET}")

        # Use a test meeting ID - these will likely fail but we want to test the endpoints
        test_past_meeting_id = "12345678901"

        result = await test_endpoint(client, "GET", f"/api/meetings/{test_past_meeting_id}/notes")
        results.append(result)
        print(f"  {result}")

        result = await test_endpoint(client, "GET", f"/api/meetings/{test_past_meeting_id}/download")
        results.append(result)
        print(f"  {result}")

        # Test 11: Recordings
        print(f"\n{Colors.BOLD}11. Recording Management{Colors.RESET}")
        result = await test_endpoint(client, "GET", "/api/recordings")
        results.append(result)
        print(f"  {result}")

    # Calculate statistics
    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed

    return results, passed, failed


async def main():
    """Main test execution."""
    try:
        results, passed, failed = await run_all_tests()

        # Print summary
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}Test Summary{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

        total = passed + failed
        pass_rate = (passed / total * 100) if total > 0 else 0

        print(f"Total Tests:  {Colors.BOLD}{total}{Colors.RESET}")
        print(f"Passed:       {Colors.GREEN}{passed} ✓{Colors.RESET}")
        print(f"Failed:       {Colors.RED}{failed} ✗{Colors.RESET}")
        print(f"Pass Rate:    {Colors.BOLD}{pass_rate:.1f}%{Colors.RESET}\n")

        if failed > 0:
            print(f"{Colors.BOLD}Failed Tests:{Colors.RESET}")
            for result in results:
                if not result.passed:
                    print(f"  {result}")
            print()

        # Exit with appropriate code
        sys.exit(0 if failed == 0 else 1)

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Testing interrupted by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Fatal error: {e}{Colors.RESET}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
