# Zope imports
from zope.interface import implements
from Products.Five import BrowserView

# Plone imports
from Products.CMFCore.interfaces import ISiteRoot

# Quills imports
from quills.core.interfaces import IWeblogArchive, ITopic, IWeblog, IWeblogEntry
from quills.core.browser.interfaces import IBaseView
from quills.app.utilities import WeblogFinder
from quills.app.utilities import getArchivePathFor, getArchiveURLFor


class BaseView(WeblogFinder, BrowserView):
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
        weblog = self.getParentWeblog(obj)
        return getArchiveURLFor(weblog, obj)
