# Zope imports
from zope.interface import implements

# Quills imports
from utilities import QuillsMixin
from utilities import recurseToInterface
from quills.core.interfaces import IWeblog
from quills.core.interfaces import IWeblogEnhanced
from quills.core.interfaces import IWeblogEntry
# Commented out to avoid circular import problems with archive and topic
# modules. The imports happen within each of the methods that require them.
#from topic import Topic, AuthorTopic

# XXX: We do need to add security assertions to this class because some
#      page templates access it even though they have been given no permission
#      to do so. Those templates should be fixed.
#      Only those methods actually accessed by restricted code are protected,
#      all other lack assertion and will deny access from restricted code.
#      Fixing this might even make acquistion unneccessary here.
from Acquisition import Implicit
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.CMFCore import permissions as permissions

# Renamed from WeblogEntryCatalogBrain to make all previous calls break.
# That way none will slip.
class CatalogBrainToWeblogEntry(QuillsMixin, Implicit):
    """Adapt a catalog brain to IWeblogEntry..

    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IWeblogEntry, CatalogBrainToWeblogEntry)
    True
    """

    security = ClassSecurityInfo()

    implements(IWeblogEntry)

    def __init__(self, brain):
        self.context = brain

    def getId(self):
        """See IWeblogEntry.
        """
        return self.context['id']

    def getTitle(self):
        """See IWeblogEntry.
        """
        return self.context['Title']

    def getTopics(self):
        """See IWeblogEntry.
        """
        from topic import Topic
        subjects = self.context['Subject']
        weblog_content = self.getWeblogContentObject()
        return [Topic(each).__of__(weblog_content) for each in subjects]

    security.declareProtected(permissions.View, "getAuthors")
    def getAuthors(self):
        """See IWeblogEntry.
        """
        from topic import AuthorTopic
        creators = self.context['listCreators']
        weblog_content = self.getWeblogContentObject()
        return [AuthorTopic(each).__of__(weblog_content) for each in creators]

    def getExcerpt(self):
        """See IWeblogEntry.
        """
        return self.context['Description']

    security.declareProtected(permissions.View, "getText")
    def getText(self):
        """See IWeblogEntry.
        """
        return self.context.getObject().getText()

    security.declareProtected(permissions.View, "getMimeType")
    def getMimeType(self):
        """See IWeblogEntry.
        """
        # In order to keep this implementation generic, we adapt the real object
        # to IWeblogEntry and just defer to that getMimeType implementation. The
        # reason being that we don't know if we're in a Quills world or a
        # QuillsEnabled world.
        return IWeblogEntry(self.context.getObject()).getMimeType()

    def getWeblogContentObject(self):
        """See IWeblogEntry.
        """
        return recurseToInterface(self.context.getObject(),
                                  (IWeblog, IWeblogEnhanced))
        
    def getWeblogEntryContentObject(self):
        """See IWeblogEntry
        """
        return self.context.getObject()

    def _getWeblogEntry(self):
        return IWeblogEntry(self.context.getObject())

    def getPublicationDate(self):
        """See IWeblogEntry.
        """
        return self.context['effective']

    def setTitle(self, title):
        """See IWeblogEntry.
        """
        self._getWeblogEntry().setTitle(title)

    def setTopics(self, topic_ids):
        """See IWeblogEntry.
        """
        self._getWeblogEntry().setTopics(topic_ids)

    def setExcerpt(self, excerpt):
        """See IWeblogEntry.
        """
        self._getWeblogEntry().setExcerpt(excerpt)

    def setText(self, text, mimetype=None):
        """See IWeblogEntry.
        """
        self._getWeblogEntry().setText(text, mimetype=mimetype)

    def edit(self, title, excerpt, text, topics, mimetype=None):
        """See IWeblogEntry.
        """
        self._getWeblogEntry().edit(title, excerpt, text,
                                            topics, mimetype=mimetype)

    def setPublicationDate(self, datetime):
        """See IWeblogEntry.
        """
        self._getWeblogEntry().setPublicationDate(datetime)

    def publish(self, pubdate=None):
        """See IWeblogEntry.
        """
        self._getWeblogEntry().publish(pubdate)

    def retract(self):
        """See IWeblogEntry.
        """
        self._getWeblogEntry().retract()

    def isPublished(self):
        """See IWeblogEntry.
        """
        self._getWeblogEntry().isPublished()

InitializeClass(CatalogBrainToWeblogEntry)
