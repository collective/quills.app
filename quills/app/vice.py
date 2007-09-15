# Zope imports
from zope.component import adapts
from zope.interface import implements

# Vice imports
from plone.syndication.outbound.interfaces import IFeed, IFeedItem
from plone.app.syndication.outbound.adapters.atct import ATFeedItemBase, ATFolderFeed

# Quills imports
from quills.core.interfaces import IWeblog, IWeblogEntry


class WeblogFeed(ATFolderFeed):
    """Adapter from IWeblog to IFeed.
    """

    implements(IFeed)
    adapts(IWeblog)


class WeblogEntryFeedItem(ATFeedItemBase):
    """Adapter from IWeblogEntry to IFeedItem
    """

    implements(IFeedItem)
    adapts(IWeblogEntry)

    @property
    def effective(self):
        """See IFeedItem
        """
        return self.context.effective()

    @property
    def tags(self):
        """See IFeedItem
        """
        return self.context.getTopics()

    @property
    def XHTML(self):
        """See IFeedItem
        """
        return self.context.getText()
