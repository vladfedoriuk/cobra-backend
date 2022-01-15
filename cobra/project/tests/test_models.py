from django.test import TestCase
from django.utils.text import slugify

from cobra.project.factories import ProjectFactory
from cobra.project.models import Project
from cobra.user.factories import UserFactory
from cobra.user.models import CustomUser
from cobra.utils.test import fake


class ProjectModelTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()

    def test_save_without_slug(self):
        title: str = fake.sentence(nb_words=4)
        project = Project(creator=self.user, title=title)
        project.save()
        self.assertEqual(project.slug, slugify(title))

    def test_save_with_slug(self):
        title: str = fake.sentence(nb_words=4)
        slug: str = fake.slug()
        project: Project = Project(title=title, slug=slug, creator=self.user)
        project.save()
        self.assertEqual(project.slug, slug)
        self.assertNotEqual(project.slug, slugify(title))

    def test_backward_relationship(self):
        projects: list[Project] = ProjectFactory.create_batch(creator=self.user, size=4)
        self.assertIsNotNone(self.user.project_project_related)
        self.assertEqual(set(self.user.project_project_related.all()), set(projects))

    def test_owner_of_the_project_has_been_deleted(self):
        admin = CustomUser.objects.all().filter_admins().first()
        project: Project = ProjectFactory()
        creator = project.creator
        creator.delete()
        project.refresh_from_db()
        admin.refresh_from_db()
        self.assertEqual(project.creator, admin)

    def test_repr(self):
        self.assertEqual(
            repr(project := ProjectFactory()),
            f"Project(creator='{project.creator.username}', slug='{project.slug}')",
        )

    def test_str(self):
        self.assertEqual(
            str(project := ProjectFactory()),
            f"{project.creator.username}:{project.slug}",
        )
