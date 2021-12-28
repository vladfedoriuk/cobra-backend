from django.test import TestCase
from django.utils.text import slugify

from cobra.project.factories import ProjectFactory
from cobra.project.models import Project
from cobra.user.factories import UserFactory
from cobra.utils.test import fake


class ProjectModelTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()

    def test_save_without_slug(self):
        title: str = fake.sentence(nb_words=4)
        project = Project(user=self.user, title=title)
        project.save()
        self.assertEqual(project.slug, slugify(title))

    def test_save_with_slug(self):
        title: str = fake.sentence(nb_words=4)
        slug: str = fake.slug()
        project: Project = Project(title=title, slug=slug, user=self.user)
        project.save()
        self.assertEqual(project.slug, slug)
        self.assertNotEqual(project.slug, slugify(title))

    def test_backward_relationship(self):
        projects: list[Project] = ProjectFactory.create_batch(user=self.user, size=4)
        self.assertIsNotNone(self.user.project_project_related)
        self.assertEqual(set(self.user.project_project_related.all()), set(projects))

    def test_repr(self):
        self.assertEqual(
            repr(project := ProjectFactory()),
            f"Project(user='{project.user.username}', slug='{project.slug}')",
        )

    def test_str(self):
        self.assertEqual(
            str(project := ProjectFactory()), f"{project.user.username}:{project.slug}"
        )
