import time
import random
import sys
import traceback
from ner_in_docker.use_cases.GroupNamedEntitiesUseCase import GroupNamedEntitiesUseCase
from ner_in_docker.domain.NamedEntity import NamedEntity
from ner_in_docker.domain.NamedEntityType import NamedEntityType
from ner_in_docker.domain.Segment import Segment
from pdf_token_type_labels import TokenType
from pdf_features.Rectangle import Rectangle


def generate_test_entities(count: int) -> list[NamedEntity]:
    entities = []

    person_names = [
        "John Smith",
        "Jane Doe",
        "Michael Johnson",
        "Sarah Williams",
        "Robert Brown",
        "Maria Garcia",
        "James Wilson",
        "Emma Martinez",
        "William Jones",
        "Olivia Davis",
        "David Miller",
        "Sophia Anderson",
        "Richard Taylor",
        "Isabella Thomas",
        "Joseph Jackson",
        "Mia White",
        "Charles Harris",
        "Charlotte Martin",
        "Christopher Thompson",
        "Amelia Garcia",
    ]

    organizations = [
        "Microsoft Corporation",
        "Apple Inc",
        "Google LLC",
        "Amazon.com",
        "Meta Platforms",
        "Tesla Inc",
        "Netflix Inc",
        "Adobe Systems",
        "Oracle Corporation",
        "IBM Corporation",
        "Intel Corporation",
        "Cisco Systems",
        "Samsung Electronics",
        "Sony Corporation",
        "Toyota Motor",
        "General Motors",
        "Ford Motor Company",
        "Boeing Company",
        "Lockheed Martin",
        "Raytheon Technologies",
    ]

    locations = [
        "New York",
        "London",
        "Paris",
        "Tokyo",
        "Berlin",
        "Rome",
        "Madrid",
        "Amsterdam",
        "Brussels",
        "Vienna",
        "Stockholm",
        "Copenhagen",
        "Oslo",
        "Helsinki",
        "Dublin",
        "Lisbon",
        "Athens",
        "Prague",
        "Warsaw",
        "Budapest",
    ]

    dates = [
        "January 15, 2023",
        "March 20, 2024",
        "July 4, 2022",
        "December 31, 2023",
        "May 1, 2024",
        "August 15, 2023",
        "September 30, 2022",
        "October 12, 2024",
        "November 25, 2023",
        "February 14, 2024",
    ]

    laws = [
        "General Data Protection Regulation",
        "GDPR Article 5",
        "CCPA Section 1798.100",
        "HIPAA Privacy Rule",
        "Sarbanes-Oxley Act",
        "Dodd-Frank Act",
        "Sherman Antitrust Act",
        "Clean Air Act",
        "Fair Labor Standards Act",
        "Americans with Disabilities Act",
    ]

    references = [
        "Section 1.1",
        "Article 5.2",
        "Clause 3.4",
        "Paragraph 2.1",
        "Chapter 7",
        "Section 4.5",
        "Article 12.3",
        "Clause 8.1",
        "Paragraph 9.2",
        "Chapter 3",
    ]

    entity_types_data = [
        (NamedEntityType.PERSON, person_names),
        (NamedEntityType.ORGANIZATION, organizations),
        (NamedEntityType.LOCATION, locations),
        (NamedEntityType.DATE, dates),
        (NamedEntityType.LAW, laws),
        (NamedEntityType.REFERENCE, references),
    ]

    segment = Segment(
        text="This is a sample segment text for testing purposes.",
        type=TokenType.TEXT,
        page_number=1,
        segment_number=0,
        bounding_box=Rectangle.from_width_height(left=0, top=0, width=100, height=20),
    )

    for i in range(count):
        entity_type, data_list = random.choice(entity_types_data)
        base_text = random.choice(data_list)

        variation = random.choice(
            [
                base_text,
                base_text.upper(),
                base_text.lower(),
                base_text + " ",
                " " + base_text,
                base_text.replace(" ", "  "),
            ]
        )

        entity = NamedEntity(
            type=entity_type,
            text=variation,
            character_start=i * 10,
            character_end=i * 10 + len(variation),
            segment_type=random.choice([TokenType.TEXT, TokenType.TITLE, TokenType.PAGE_HEADER]),
            segment=segment,
            relevance_percentage=random.randint(0, 100),
        )
        entities.append(entity)

    return entities


def generate_test_entities_by_type(count: int, entity_type: NamedEntityType) -> list[NamedEntity]:
    entities = []

    person_names = [
        "John Smith",
        "Jane Doe",
        "Michael Johnson",
        "Sarah Williams",
        "Robert Brown",
        "Maria Garcia",
        "James Wilson",
        "Emma Martinez",
        "William Jones",
        "Olivia Davis",
        "David Miller",
        "Sophia Anderson",
        "Richard Taylor",
        "Isabella Thomas",
        "Joseph Jackson",
        "Mia White",
        "Charles Harris",
        "Charlotte Martin",
        "Christopher Thompson",
        "Amelia Garcia",
    ]

    organizations = [
        "Microsoft Corporation",
        "Apple Inc",
        "Google LLC",
        "Amazon.com",
        "Meta Platforms",
        "Tesla Inc",
        "Netflix Inc",
        "Adobe Systems",
        "Oracle Corporation",
        "IBM Corporation",
        "Intel Corporation",
        "Cisco Systems",
        "Samsung Electronics",
        "Sony Corporation",
        "Toyota Motor",
        "General Motors",
        "Ford Motor Company",
        "Boeing Company",
        "Lockheed Martin",
        "Raytheon Technologies",
    ]

    locations = [
        "New York",
        "London",
        "Paris",
        "Tokyo",
        "Berlin",
        "Rome",
        "Madrid",
        "Amsterdam",
        "Brussels",
        "Vienna",
        "Stockholm",
        "Copenhagen",
        "Oslo",
        "Helsinki",
        "Dublin",
        "Lisbon",
        "Athens",
        "Prague",
        "Warsaw",
        "Budapest",
    ]

    dates = [
        "January 15, 2023",
        "March 20, 2024",
        "July 4, 2022",
        "December 31, 2023",
        "May 1, 2024",
        "August 15, 2023",
        "September 30, 2022",
        "October 12, 2024",
        "November 25, 2023",
        "February 14, 2024",
    ]

    laws = [
        "General Data Protection Regulation",
        "GDPR Article 5",
        "CCPA Section 1798.100",
        "HIPAA Privacy Rule",
        "Sarbanes-Oxley Act",
        "Dodd-Frank Act",
        "Sherman Antitrust Act",
        "Clean Air Act",
        "Fair Labor Standards Act",
        "Americans with Disabilities Act",
    ]

    references = [
        "Section 1.1",
        "Article 5.2",
        "Clause 3.4",
        "Paragraph 2.1",
        "Chapter 7",
        "Section 4.5",
        "Article 12.3",
        "Clause 8.1",
        "Paragraph 9.2",
        "Chapter 3",
    ]

    type_to_data = {
        NamedEntityType.PERSON: person_names,
        NamedEntityType.ORGANIZATION: organizations,
        NamedEntityType.LOCATION: locations,
        NamedEntityType.DATE: dates,
        NamedEntityType.LAW: laws,
        NamedEntityType.REFERENCE: references,
    }

    data_list = type_to_data[entity_type]

    segment = Segment(
        text="This is a sample segment text for testing purposes.",
        type=TokenType.TEXT,
        page_number=1,
        segment_number=0,
        bounding_box=Rectangle.from_width_height(left=0, top=0, width=100, height=20),
    )

    for i in range(count):
        base_text = random.choice(data_list)

        variation = random.choice(
            [
                base_text,
                base_text.upper(),
                base_text.lower(),
                base_text + " ",
                " " + base_text,
                base_text.replace(" ", "  "),
            ]
        )

        entity = NamedEntity(
            type=entity_type,
            text=variation,
            character_start=i * 10,
            character_end=i * 10 + len(variation),
            segment_type=random.choice([TokenType.TEXT, TokenType.TITLE, TokenType.PAGE_HEADER]),
            segment=segment,
            relevance_percentage=random.randint(0, 100),
        )
        entities.append(entity)

    return entities


def benchmark_grouping():
    try:
        print("=" * 80)
        print("BENCHMARKING GroupNamedEntitiesUseCase.group() - 250 entities per type")
        print("=" * 80)
        sys.stdout.flush()

        entity_types = [
            NamedEntityType.PERSON,
            NamedEntityType.ORGANIZATION,
            NamedEntityType.LOCATION,
            NamedEntityType.DATE,
            NamedEntityType.LAW,
            NamedEntityType.REFERENCE,
        ]

        results = []
        entities_per_type = 250

        for entity_type in entity_types:
            print(f"\n{'=' * 80}")
            print(f"Testing {entity_type} with {entities_per_type} entities")
            print(f"{'=' * 80}")
            sys.stdout.flush()

            entities = generate_test_entities_by_type(entities_per_type, entity_type)

            print(f"Generated {len(entities)} entities of type {entity_type}")
            sys.stdout.flush()

            use_case = GroupNamedEntitiesUseCase()

            start_time = time.time()
            groups = use_case.group(entities)
            elapsed_time = time.time() - start_time

            print(f"Total groups created: {len(groups)}")
            print(f"Time: {elapsed_time:.4f} seconds")
            sys.stdout.flush()

            results.append({"type": entity_type, "entities": entities_per_type, "groups": len(groups), "time": elapsed_time})

        print(f"\n\n{'=' * 80}")
        print("SUMMARY - TIME PER GROUP TYPE")
        print(f"{'=' * 80}")
        print(f"{'Entity Type':<20} {'Entities':<12} {'Groups':<12} {'Time (s)':<15}")
        print(f"{'-' * 20} {'-' * 12} {'-' * 12} {'-' * 15}")
        for result in results:
            print(f"{result['type']:<20} {result['entities']:<12} {result['groups']:<12} {result['time']:<15.4f}")

        print(f"\n{'=' * 80}")
        total_time = sum(r["time"] for r in results)
        total_entities = sum(r["entities"] for r in results)
        total_groups = sum(r["groups"] for r in results)
        print(f"TOTAL TIME: {total_time:.4f} seconds")
        print(f"TOTAL ENTITIES: {total_entities}")
        print(f"TOTAL GROUPS: {total_groups}")
        print(f"{'=' * 80}")
        sys.stdout.flush()

    except Exception as e:
        print(f"\nERROR: {e}")
        print(f"\nTraceback:")
        traceback.print_exc()
        sys.stdout.flush()


if __name__ == "__main__":
    benchmark_grouping()
