from unittest import TestCase

from domain.NamedEntityGroup import NamedEntityGroup
from domain.NamedEntityType import NamedEntityType
from domain.PDFNamedEntity import PDFNamedEntity
from ports.PDFsGroupNameRepository import PDFsGroupNameRepository
from use_cases.PDFNamedEntityMergerUseCase import PDFNamedEntityMergerUseCase


class InMemoryPDFsGroupNameRepository(PDFsGroupNameRepository):
    def __init__(self):
        self.groups_in_memory = []

    def update_groups_by_old_groups(self, named_entity_groups: list[NamedEntityGroup]):
        groups_with_in_memory_name = []
        for group in named_entity_groups:
            groups_with_in_memory_name.append(group)
            for group_in_memory in self.groups_in_memory:
                if group_in_memory.is_same_group(group):
                    groups_with_in_memory_name[-1].name = group_in_memory.name
                    break

            self.groups_in_memory.append(group)

        return groups_with_in_memory_name

    def get_reference_destinations(self) -> list[NamedEntityGroup]:
        return []


class TestPDFNamedEntityMergerUseCase(TestCase):
    def test_merge_entities(self):
        name_entity_1 = PDFNamedEntity(type=NamedEntityType.PERSON, text="María Diaz")
        name_entity_2 = PDFNamedEntity(type=NamedEntityType.PERSON, text="María Diaz")
        name_entity_3 = PDFNamedEntity(type=NamedEntityType.PERSON, text="Other Name")
        in_memory_repository = InMemoryPDFsGroupNameRepository()
        pdf_named_entity_merger_use_case = PDFNamedEntityMergerUseCase(in_memory_repository)
        named_entities_grouped = pdf_named_entity_merger_use_case.merge([name_entity_1, name_entity_2, name_entity_3])

        self.assertEqual(2, len(named_entities_grouped))
        self.assertEqual("María Diaz", named_entities_grouped[0].name)
        self.assertEqual(NamedEntityType.PERSON, named_entities_grouped[0].type)
        self.assertEqual(2, len(named_entities_grouped[0].named_entities))
        self.assertEqual(PDFNamedEntity, type(named_entities_grouped[0].named_entities[0]))
        self.assertEqual("María Diaz", named_entities_grouped[0].named_entities[0].text)
        self.assertEqual(PDFNamedEntity, type(named_entities_grouped[0].named_entities[1]))
        self.assertEqual("María Diaz", named_entities_grouped[0].named_entities[1].text)

        self.assertEqual("Other Name", named_entities_grouped[1].name)
        self.assertEqual(NamedEntityType.PERSON, named_entities_grouped[1].type)
        self.assertEqual(1, len(named_entities_grouped[1].named_entities))
        self.assertEqual("Other Name", named_entities_grouped[1].named_entities[0].text)

    def test_merge_entities_using_previous_pdfs(self):
        in_memory_repository = InMemoryPDFsGroupNameRepository()
        pdf_named_entity_merger_use_case = PDFNamedEntityMergerUseCase(in_memory_repository)

        name_entity_1 = PDFNamedEntity(type=NamedEntityType.PERSON, text="María Diaz Perez")
        pdf_named_entity_merger_use_case.merge([name_entity_1])

        name_entity_2 = PDFNamedEntity(type=NamedEntityType.PERSON, text="María Diaz")
        named_entities_grouped = pdf_named_entity_merger_use_case.merge([name_entity_2])

        self.assertEqual(1, len(named_entities_grouped))
        self.assertEqual("María Diaz Perez", named_entities_grouped[0].name)
        self.assertEqual(NamedEntityType.PERSON, named_entities_grouped[0].type)
        self.assertEqual(1, len(named_entities_grouped[0].named_entities))
        self.assertEqual(PDFNamedEntity, type(named_entities_grouped[0].named_entities[0]))
        self.assertEqual("María Diaz", named_entities_grouped[0].named_entities[0].text)
