# Zope imports
from zope.interface import Interface


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
