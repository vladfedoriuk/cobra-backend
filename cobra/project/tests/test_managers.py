from django.test import TestCase
from faker.utils.text import slugify

from cobra.project.models import Project
from cobra.user.factories import UserFactory
from cobra.utils.test import fake


class ProjectManagerTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()

    def test_create_without_slug(self):
        title: str = fake.sentence(nb_words=4)
        project: Project = Project.objects.create(title=title, user=self.user)
        self.assertEqual(project.title, title)
        self.assertEqual(project.slug, slugify(title))

    def test_create_with_slug(self):
        title: str = fake.sentence(nb_words=4)
        slug: str = fake.slug()
        project: Project = Project.objects.create(
            title=title, slug=slug, user=self.user
        )
        self.assertEqual(project.slug, slug)
        self.assertNotEqual(project.slug, slugify(project.title))

    def test_bulk_create(self):
        projects: list[Project] = [
            Project(title=fake.sentence(nb_words=4), user=self.user) for _ in range(4)
        ]
        Project.objects.bulk_create(projects)
        for project in projects:
            project.refresh_from_db(fields=["slug"])
            self.assertEqual(project.slug, slugify(project.title))

    def test_get_or_create(self):
        title: str = fake.sentence(nb_words=4)
        project, created = Project.objects.get_or_create(user=self.user, title=title)
        self.assertTrue(created)
        self.assertEqual(project.slug, slugify(project.title))

    def test_update_or_create(self):
        title: str = fake.sentence(nb_words=4)
        project, created = Project.objects.update_or_create(user=self.user, title=title)
        self.assertTrue(created)
        self.assertEqual(project.slug, slugify(project.title))
