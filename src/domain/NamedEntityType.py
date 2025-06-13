from enum import StrEnum


class NamedEntityType(StrEnum):
    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"
    LOCATION = "LOCATION"
    DATE = "DATE"
    LAW = "LAW"
    REFERENCE_DESTINATION = "REFERENCE_DESTINATION"
    REFERENCE_POINTER = "REFERENCE_POINTER"

    @staticmethod
    def from_flair_type(flair_type: str):
        str_to_entity_type = {
            "ORG": NamedEntityType.ORGANIZATION,
            "PERSON": NamedEntityType.PERSON,
            "LAW": NamedEntityType.LAW,
            "GPE": NamedEntityType.LOCATION,
        }
        return str_to_entity_type[flair_type]
