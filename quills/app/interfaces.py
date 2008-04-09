# Zope imports
from zope.interface import Interface
from zope import schema
from zope.i18nmessageid import MessageFactory

# quills imports
from quills.core.interfaces import IWeblogConfiguration


class ITransientTopicContainer(Interface):
    """A marker interface that allows us to distinguish between IWeblog, which
    subclasses ITopicContainer, and the transient ITopicContainer implementation
    for the purposes of avoiding maximum recursion errors in the portlets
    machinery.
    """


class ITransientAuthorContainer(Interface):
    """A marker interface that allows us to distinguish between IWeblog, which
    subclasses IAuthorContainer, and the transient IAuthorContainer
    implementation for the purposes of avoiding maximum recursion errors in the
    portlets machinery.
    """

class ITransientArchive(Interface):
    """A marker interface that allows us to distinguish between IWeblog, which
    subclasses IWeblogArchive, and the transient IWeblogArchive implementation
    for the purposes of avoiding maximum recursion errors in the portlets
    machinery.
    """


_ = MessageFactory('quills')

class IDefaultTypeAwareWeblogConfiguration(IWeblogConfiguration):
    """
    """

    default_type = schema.TextLine(
        title=_(u'Default type.'),
        description=_(u'The default portal_type to add for this weblog.'),
        default=u'Document',
        required=False,
        )


class IStateAwareWeblogConfiguration(IWeblogConfiguration):
    """
    """

    published_states = schema.List(
        title=_(u'Published workflow states'),
        description=_(u'Workflow states to treat as published.'),
        default=[u'published'],
        required=True,
        value_type=schema.TextLine(),
        )

    draft_states = schema.List(
        title=_(u'Draft workflow states'),
        description=_(u'Workflow states to treat as draft.'),
        default=[u'private'],
        required=True,
        value_type=schema.TextLine(),
        )


class IWeblogEnhancedConfiguration(IDefaultTypeAwareWeblogConfiguration,
                                   IStateAwareWeblogConfiguration):
    """
    """
    pass
