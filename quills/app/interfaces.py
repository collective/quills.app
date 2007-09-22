# Zope imports
from zope.interface import Interface


class ITransientTopicContainer(Interface):
    """An marker interface that allows us to distinguish between IWeblog, which
    subclasses ITopicContainer, and the transient ITopicContainer implementation
    for the purposes of avoiding maximum recursion errors in the portlets
    machinery.
    """


class ITransientAuthorContainer(Interface):
    """An marker interface that allows us to distinguish between IWeblog, which
    subclasses IAuthorContainer, and the transient IAuthorContainer
    implementation for the purposes of avoiding maximum recursion errors in the
    portlets machinery.
    """
