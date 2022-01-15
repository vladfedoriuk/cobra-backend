from operator import itemgetter

import factory.fuzzy
from factory.django import DjangoModelFactory

from cobra.project.models import ROLES, Project, ProjectMembership
from cobra.user.factories import UserFactory


class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = Project

    title = factory.Faker("sentence", nb_words=4)
    creator = factory.SubFactory(UserFactory)

    @factory.post_generation
    def members(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of users were passed in, use them
            for user in extracted:
                ProjectMembershipFactory.create(user=user, project=self)


class ProjectMembershipFactory(DjangoModelFactory):
    class Meta:
        model = ProjectMembership

    user = factory.SubFactory(UserFactory)
    project = factory.SubFactory(ProjectFactory)
    role = factory.fuzzy.FuzzyChoice(ROLES, getter=itemgetter(0))
