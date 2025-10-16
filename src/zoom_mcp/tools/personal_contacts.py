"""
Personal Contacts Lookup Tool

Search personal contacts from CSV file for meeting creation.
"""

import csv
from pathlib import Path
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class SearchContactParams(BaseModel):
    """Parameters for searching personal contacts."""
    query: str = Field(
        description="Search query - name, email, or company"
    )


class Contact(BaseModel):
    """Personal contact information."""
    name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None


def load_contacts() -> List[Contact]:
    """Load personal contacts from CSV file."""
    contacts_file = Path(__file__).parent.parent.parent / "personal_contacts.csv"

    if not contacts_file.exists():
        return []

    contacts = []
    with open(contacts_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            contacts.append(Contact(
                name=row['name'],
                email=row['email'],
                phone=row.get('phone', ''),
                company=row.get('company', '')
            ))

    return contacts


async def search_personal_contacts(params: SearchContactParams) -> dict:
    """
    Search personal contacts by name, email, or company.

    Args:
        params: Search parameters

    Returns:
        Dictionary containing matching contacts
    """
    contacts = load_contacts()
    query = params.query.lower()

    matches = []
    for contact in contacts:
        if (query in contact.name.lower() or
            query in contact.email.lower() or
            (contact.company and query in contact.company.lower())):
            matches.append(contact.dict())

    return {
        "query": params.query,
        "total_matches": len(matches),
        "contacts": matches
    }


async def get_contact_by_name(name: str) -> Optional[Dict]:
    """
    Get contact by exact or partial name match.

    Args:
        name: Contact name to search for

    Returns:
        Contact dict if found, None otherwise
    """
    contacts = load_contacts()
    name_lower = name.lower()

    # Try exact match first
    for contact in contacts:
        if contact.name.lower() == name_lower:
            return contact.dict()

    # Try partial match
    for contact in contacts:
        if name_lower in contact.name.lower():
            return contact.dict()

    return None
