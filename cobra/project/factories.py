from operator import itemgetter

import factory.fuzzy
from factory.django import DjangoModelFactory

from cobra.project.models import (
    ROLES,
    Epic,
    Issue,
    Project,
    ProjectInvitation,
    ProjectMembership,
)
from cobra.project.utils.models import INVITATION_STATUSES, TASK_STATUSES, TASK_TYPES
from cobra.user.factories import UserFactory


class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = Project

    creator = factory.SubFactory(UserFactory)
    title = factory.Faker("sentence", nb_words=4)
    description = factory.fuzzy.FuzzyText()

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
    role = factory.fuzzy.FuzzyChoice(ROLES, getter=itemgetter(0))


class ProjectInvitationFactory(DjangoModelFactory):
    class Meta:
        model = ProjectInvitation

    inviter = factory.SubFactory(UserFactory)
    status = factory.fuzzy.FuzzyChoice(INVITATION_STATUSES, getter=itemgetter(0))
    user = factory.SubFactory(UserFactory)
    project = factory.SubFactory(ProjectFactory)


class EpicFactory(DjangoModelFactory):
    class Meta:
        model = Epic

    creator = factory.SubFactory(UserFactory)
    project = factory.SubFactory(ProjectFactory)
    title = factory.Faker("sentence", nb_words=4)
    description = factory.fuzzy.FuzzyText()


class IssueFactory(DjangoModelFactory):
    class Meta:
        model = Issue

    creator = factory.SubFactory(UserFactory)
    project = factory.SubFactory(ProjectFactory)
    title = factory.Faker("sentence", nb_words=4)
    description = factory.fuzzy.FuzzyText()
    status = factory.fuzzy.FuzzyChoice(TASK_STATUSES, getter=itemgetter(0))
    type = factory.fuzzy.FuzzyChoice(TASK_TYPES, getter=itemgetter(0))
    estimate = factory.fuzzy.FuzzyDecimal(low=0)
    parent = factory.LazyAttribute(lambda x: IssueFactory(parent=None))
    epic = factory.SubFactory(EpicFactory)
