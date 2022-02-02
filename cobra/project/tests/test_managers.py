from django.test import TestCase
from faker.utils.text import slugify
from parameterized import parameterized

from cobra.project.factories import (
    IssueFactory,
    ProjectFactory,
    ProjectMembershipFactory,
)
from cobra.project.models import Issue, Project, ProjectMembership
from cobra.project.utils.models import DEVELOPER, MAINTAINER
from cobra.user.factories import UserFactory
from cobra.utils.test import fake


class ProjectManagerTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()

    def test_create_without_slug(self):
        title: str = fake.sentence(nb_words=4)
        project: Project = Project.objects.create(title=title, creator=self.user)
        self.assertEqual(project.title, title)
        self.assertEqual(project.slug, slugify(title))

    def test_create_with_slug(self):
        title: str = fake.sentence(nb_words=4)
        slug: str = fake.slug()
        project: Project = Project.objects.create(
            title=title, slug=slug, creator=self.user
        )
        self.assertEqual(project.slug, slug)
        self.assertNotEqual(project.slug, slugify(project.title))

    def test_bulk_create(self):
        projects: list[Project] = [
            Project(title=fake.sentence(nb_words=4), creator=self.user)
            for _ in range(4)
        ]
        Project.objects.bulk_create(projects)
        for project in projects:
            project.refresh_from_db(fields=["slug"])
            self.assertEqual(project.slug, slugify(project.title))

    def test_get_or_create(self):
        title: str = fake.sentence(nb_words=4)
        project, created = Project.objects.get_or_create(creator=self.user, title=title)
        self.assertTrue(created)
        self.assertEqual(project.slug, slugify(project.title))

    def test_update_or_create(self):
        title: str = fake.sentence(nb_words=4)
        project, created = Project.objects.update_or_create(
            creator=self.user, title=title
        )
        self.assertTrue(created)
        self.assertEqual(project.slug, slugify(project.title))


class ProjectMembershipManagerTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.project = ProjectFactory()

    @parameterized.expand(
        [
            (None, None, True),
            (UserFactory, None, False),
            (None, ProjectFactory, False),
            (UserFactory, ProjectFactory, False),
        ]
    )
    def test_is_user_project_member(self, user, project, is_member):
        ProjectMembershipFactory.create(user=self.user, project=self.project)
        self.assertTrue(
            ProjectMembership.objects.is_user_project_member(
                user() if user else self.user, project() if project else self.project
            )
            is is_member
        )

    @parameterized.expand(
        [
            (None, None, True),
            (UserFactory, None, False),
            (None, ProjectFactory, False),
            (UserFactory, ProjectFactory, False),
        ]
    )
    def test_is_user_project_developer(self, user, project, is_developer):
        ProjectMembershipFactory.create(
            project=self.project,
            user=self.user,
            role=DEVELOPER,
        )
        self.assertTrue(
            ProjectMembership.objects.is_user_project_developer(
                user() if user else self.user, project() if project else self.project
            )
            is is_developer
        )

    @parameterized.expand(
        [
            (None, None, True),
            (UserFactory, None, False),
            (None, ProjectFactory, False),
            (UserFactory, ProjectFactory, False),
        ]
    )
    def test_is_user_project_maintainer(self, user, project, is_maintainer):
        ProjectMembershipFactory.create(
            project=self.project,
            user=self.user,
            role=MAINTAINER,
        )
        self.assertTrue(
            ProjectMembership.objects.is_user_project_maintainer(
                user() if user else self.user, project() if project else self.project
            )
            is is_maintainer
        )

    @parameterized.expand(
        [
            (None, "is_user_project_member_or_creator"),
            (DEVELOPER, "is_user_project_developer_or_creator"),
            (MAINTAINER, "is_user_project_maintainer_or_creator"),
        ]
    )
    def test_is_user_project_member_or_creator(self, role, method_name):
        project = ProjectFactory()
        project_membership = ProjectMembershipFactory(project=project)
        if role is not None:
            project_membership.role = role
            project_membership.save(update_fields=["role"])
        method = getattr(ProjectMembership.objects, method_name)
        self.assertTrue(method(project.creator, project))
        self.assertTrue(method(project_membership.user, project))


class IssueManagerTest(TestCase):
    def test_filter_for_project(self):
        project = ProjectFactory()
        issue = IssueFactory(project=project)
        self.assertEqual(Issue.objects.filter_for_project(project).first(), issue)
