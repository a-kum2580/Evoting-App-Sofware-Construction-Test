"""Candidate domain model."""

import datetime


class Candidate:
    """Represents an election candidate."""

    def __init__(self, candidate_id, full_name, national_id, date_of_birth,
                 age, gender, education, party, manifesto, address, phone,
                 email, has_criminal_record=False, years_experience=0,
                 is_active=True, is_approved=True, created_at=None,
                 created_by=None):
        self.id = candidate_id
        self.full_name = full_name
        self.national_id = national_id
        self.date_of_birth = date_of_birth
        self.age = age
        self.gender = gender
        self.education = education
        self.party = party
        self.manifesto = manifesto
        self.address = address
        self.phone = phone
        self.email = email
        self.has_criminal_record = has_criminal_record
        self.years_experience = years_experience
        self.is_active = is_active
        self.is_approved = is_approved
        self.created_at = created_at or str(datetime.datetime.now())
        self.created_by = created_by

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "national_id": self.national_id,
            "date_of_birth": self.date_of_birth,
            "age": self.age,
            "gender": self.gender,
            "education": self.education,
            "party": self.party,
            "manifesto": self.manifesto,
            "address": self.address,
            "phone": self.phone,
            "email": self.email,
            "has_criminal_record": self.has_criminal_record,
            "years_experience": self.years_experience,
            "is_active": self.is_active,
            "is_approved": self.is_approved,
            "created_at": self.created_at,
            "created_by": self.created_by,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            candidate_id=data["id"],
            full_name=data["full_name"],
            national_id=data["national_id"],
            date_of_birth=data["date_of_birth"],
            age=data["age"],
            gender=data["gender"],
            education=data["education"],
            party=data["party"],
            manifesto=data["manifesto"],
            address=data["address"],
            phone=data["phone"],
            email=data["email"],
            has_criminal_record=data.get("has_criminal_record", False),
            years_experience=data.get("years_experience", 0),
            is_active=data.get("is_active", True),
            is_approved=data.get("is_approved", True),
            created_at=data.get("created_at"),
            created_by=data.get("created_by"),
        )
