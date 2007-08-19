# Zope imports
from zope.interface import implements

# Quills imports
from utilities import QuillsMixin, recurseToInterface
from quills.core.interfaces import IWeblog, IWeblogEnhanced, IWeblogEntry
# Commented out to avoid circular import problems with archive and topic
# modules. The imports happen within each of the methods that require them.
#from topic import Topic, AuthorTopic


class WeblogEntryCatalogBrain(QuillsMixin):
    """A catalog brain that implements IWeblogEntry (in and efficient way).
    """

    implements(IWeblogEntry)

    def getTitle(self):
        """See IWeblogEntry.
        """
        return self['Title']

    def getTopics(self):
        """See IWeblogEntry.
        """
        from topic import Topic
        subjects = self['Subject']
        weblog_content = self.getParentWeblogContentObject()
        return [Topic(each).__of__(weblog_content) for each in subjects]

    def getAuthors(self):
        """See IWeblogEntry.
        """
        from topic import AuthorTopic
        creators = self['creators']
        weblog_content = self.getParentWeblogContentObject()
        return [AuthorTopic(each).__of__(weblog_content) for each in creators]

    def getExcerpt(self):
        """See IWeblogEntry.
        """
        return self['Description']

    def getText(self):
        """See IWeblogEntry.
        """
        return self._getObject().getText()

    def getParentWeblogContentObject(self):
        """
        """
        return recurseToInterface(self._getObject(), (IWeblog, IWeblogEnhanced))

    def _getObject(self):
        #if getattr(self, '__object', None) is None:
        #    self.__object = self.getObject()
        #return self.__object
        return self.getObject()

    def _getWeblogEntry(self):
        return IWeblogEntry(self.getObject())

    def getPublicationDate(self):
        """Return a DateTime instance for when this IWeblogEntry was/will-be
        published.
        """
        return self['effective']

    def setTitle(title):
        """
        """
        self._getWeblogEntry().setTitle(title)

    def setTopics(topic_ids):
        """
        """
        self._getWeblogEntry().setTopics(topic_ids)

    def setExcerpt(excerpt):
        """
        """
        self._getWeblogEntry().setExcerpt(excerpt)

    def setText(text):
        """
        """
        self._getWeblogEntry().setText(text)

    def edit(self, title, excerpt, text, topics):
        """
        """
        self._getWeblogEntry().edit(title, excerpt, text, topics)

    def setPublicationDate(datetime):
        """Set when this IWeblogEntry was/will-be published.
        """
        self._getWeblogEntry().setPublicationDate(datetime)

    def publish(pubdate=None):
        """Publish this weblog entry.  Do nothing if it is already published.
        `pubdate' defaults to datetime.now().
        """
        self._getWeblogEntry().publish(pubdate)

    def retract():
        """Retract this weblog entry to 'draft' status.  Do nothing if it is
        already a draft.
        """
        self._getWeblogEntry().retract()

    def isPublished():
        """Return True if this weblog entry is currently published, False
        otherwise.
        """
        return self['review_state'] == 'published'
