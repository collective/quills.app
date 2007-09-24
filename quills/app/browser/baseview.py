# Zope imports
from zope.interface import implements
from Products.Five import BrowserView
from Products.ZCatalog.CatalogBrains import AbstractCatalogBrain

# Plone imports
from Products.CMFCore.utils import getToolByName

# Quills imports
from quills.core.interfaces import IWeblogArchive, ITopic, IWeblog, IWeblogEntry
from quills.core.browser.interfaces import IBaseView
from quills.app.utilities import getArchivePathFor, getArchiveURLFor
from quills.app.weblogentrybrain import WeblogEntryCatalogBrain


class BaseView(BrowserView):
    """A class with helper methods for use in views/templates.
    """

    implements(IBaseView)

    def isWeblogContent(self, obj=None):
        """See IBaseView.
        """
        if obj is None:
            obj = self.context
        if IWeblog.providedBy(obj):
            return True
        elif IWeblogArchive.providedBy(obj):
            return True
        elif IWeblogEntry.providedBy(obj):
            return True
        elif ITopic.providedBy(obj):
            return True
        return False

    def getArchivePathFor(self, obj):
        """See IWeblogView.
        """
        return getArchivePathFor(obj)

    def getArchiveURLFor(self, obj):
        """See IWeblogView.
        """
        weblog_content = obj.getWeblogContentObject()
        return getArchiveURLFor(obj, weblog_content)

    def displayingOneEntry(self, context, weblogentry):
        """See IWeblogView.
        """
        entry_absolute_url = getattr(weblogentry, 'absolute_url', None)
        if entry_absolute_url is None:
            entry_absolute_url = weblogentry.context.absolute_url
        return context.absolute_url() == entry_absolute_url()

    def isDiscussionAllowedFor(self, obj):
        """
        """
        dtool = getToolByName(self.context, 'portal_discussion')
        if isinstance(obj, AbstractCatalogBrain):
            obj = obj.getObject()
        return dtool.isDiscussionAllowedFor(obj)

    def getCommentCountFor(self, obj):
        """
        """
        dtool = getToolByName(self.context, 'portal_discussion')
        if isinstance(obj, AbstractCatalogBrain):
            obj = obj.getObject()
        return dtool.getDiscussionFor(obj).replyCount(obj)
