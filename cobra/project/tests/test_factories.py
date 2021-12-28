from django.test import TestCase
from django.utils.text import slugify

from cobra.project.factories import ProjectFactory
from cobra.project.models import Project
from cobra.user.factories import UserFactory
from cobra.user.models import CustomUser
from cobra.utils.test import TestFactoryMixin, fake


class ProjectFactoryTest(TestCase, TestFactoryMixin):
    factory_class = ProjectFactory
    must_be_not_none = ["title", "user", "slug"]
    must_be_unique_together = ["user", "slug"]

    def setUp(self) -> None:
        user: CustomUser = UserFactory()
        title: str = fake.sentence(nb_words=4)
        slug: str = fake.slug()

        self.test_with_given_property = [
            ({"name": "title", "value": title}, title),
            ({"name": "user", "value": user}, user),
            ({"name": "slug", "value": slug}, slug),
        ]

    def test_slug_generated_from_title(self):
        title: str = fake.sentence(nb_words=4)
        project: Project = ProjectFactory(title=title)
        self.assertEqual(project.title, title)
        self.assertEqual(project.slug, slugify(project.title))

    def test_create_project_with_a_member(self):
        project: Project = self.factory_class.create(members=[UserFactory()])
        self.assertIsNotNone(project)
        self.assertTrue(len(project.members.all()) > 0)
        self.assertTrue(CustomUser.objects.filter(project=project).distinct().exists())

    def test_create_project_with_several_members(self):
        users: list[CustomUser] = UserFactory.create_batch(5)
        project: Project = self.factory_class.create(members=users)
        self.assertEqual(set(project.members.all()), set(users))
        for user in users:
            self.assertIn(project, user.projects.all())
