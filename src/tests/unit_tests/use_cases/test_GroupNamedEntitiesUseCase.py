from unittest import TestCase

from use_cases.GroupNamedEntitiesUseCase import GroupNamedEntitiesUseCase
from domain.NamedEntity import NamedEntity
from domain.NamedEntityType import NamedEntityType


class TestGroupNamedEntitiesUseCase(TestCase):
    def test_group_empty_entities_returns_empty_list(self):
        use_case = GroupNamedEntitiesUseCase()
        self.assertEqual(use_case.group([]), [])

    def test_date_entities_group_by_normalized_text(self):
        e1 = NamedEntity(type=NamedEntityType.DATE, text="1 Jan 2021")
        e2 = NamedEntity(type=NamedEntityType.DATE, text="2021-01-01")
        use_case = GroupNamedEntitiesUseCase()
        groups = use_case.group([e1, e2])
        self.assertEqual(len(groups), 1)
        group = groups[0]
        normalized = e1.get_with_normalize_entity_text().normalized_text
        self.assertEqual(group.name, normalized)
        self.assertCountEqual([ne.text for ne in group.named_entities], ["1 Jan 2021", "2021-01-01"])

    def test_prior_reference_grouping(self):
        prior = NamedEntity(
            type=NamedEntityType.REFERENCE, text="Section 1: Intro", group_name="Section 1: Intro", relevance_percentage=100
        )
        new_entity = NamedEntity(
            type=NamedEntityType.REFERENCE,
            text="Section 1: Intro",
            normalized_text="Section 1: Intro",
            relevance_percentage=0,
        )
        groups = GroupNamedEntitiesUseCase(prior_entities=[prior]).group([new_entity])
        self.assertEqual(len(groups), 1)
        group = groups[0]
        self.assertEqual(group.name, "Section 1: Intro")
        self.assertEqual(group.named_entities[0].text, "Section 1: Intro")
        self.assertEqual(group.top_relevance_entity.relevance_percentage, 100)
        self.assertEqual(group.top_relevance_entity.text, "Section 1: Intro")

    def test_multiple_types_independent_groups(self):
        date_ent = NamedEntity(type=NamedEntityType.DATE, text="2020-12-31")
        loc_ent = NamedEntity(type=NamedEntityType.LOCATION, text="London")
        person_ent = NamedEntity(type=NamedEntityType.PERSON, text="Alice")
        use_case = GroupNamedEntitiesUseCase()
        groups = use_case.group([date_ent, loc_ent, person_ent])
        self.assertEqual(len(groups), 3)
        names = {g.name for g in groups}
        self.assertIn(date_ent.get_with_normalize_entity_text().normalized_text, names)
        self.assertIn("London", names)
        self.assertIn("Alice", names)
