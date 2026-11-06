import json
import os
from typing import Dict, Optional

CONTACTS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "contacts.json")

def load_contacts() -> Dict[str, str]:
    if not os.path.exists(CONTACTS_FILE):
        # Default sample contacts structure
        sample = {
            "abu": "",
            "ammi": "",
            "bhai": "",
            "dost": ""
        }
        save_contacts(sample)
        return sample
    try:
        with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_contacts(contacts: Dict[str, str]):
    with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)

def get_phone_for_contact(name: str) -> Optional[str]:
    contacts = load_contacts()
    name_clean = name.lower().strip()
    return contacts.get(name_clean)

def set_contact(name: str, phone: str):
    contacts = load_contacts()
    contacts[name.lower().strip()] = phone.strip()
    save_contacts(contacts)

