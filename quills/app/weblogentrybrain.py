from zope.interface import implements

from utilities import WeblogFinder
from quills.core.interfaces import IWeblogEntry
# Commented out to avoid circular import problems with archive and topic
# modules. The imports happen within each of the methods that require them.
#from topic import Topic, AuthorTopic


class WeblogEntryCatalogBrain(WeblogFinder):
    """A catalog brain that implements IWeblogEntry (in and efficient way).
    """

    implements(IWeblogEntry)

    def getTopics(self):
        """See IWeblogEntry.
        """
        from topic import Topic
        subjects = self['Subject']
        weblog = self.getParentWeblog()
        return [Topic(each).__of__(weblog) for each in subjects]

    def getAuthors(self):
        """See IWeblogEntry.
        """
        from topic import AuthorTopic
        creators = self['creators']
        weblog = self.getParentWeblog()
        return [AuthorTopic(each).__of__(weblog) for each in creators]

    def getExcerpt(self):
        """See IWeblogEntry.
        """
        return self['Description']

    def getText(self):
        """See IWeblogEntry.
        """
        return self.getObject().getText()
