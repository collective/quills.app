# Zope imports
from zope.interface import implements

# Plone imports
from Products.CMFPlone.PloneBatch import Batch as PloneBatch
from Products.CMFCore.utils import getToolByName

# Quills imports
from quills.core.interfaces import IWeblogConfiguration
from quills.core.interfaces import IWeblogEntry
from quills.core.browser.interfaces import IWeblogView
from quills.core.browser.interfaces import IWeblogEntryView
from quills.core.browser.interfaces import ITopicView
from baseview import BaseView


class WeblogView(BaseView):
    """A class with helper methods for use in views/templates.

    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IWeblogView, WeblogView)
    True
    """

    implements(IWeblogView)

    def getConfig(self):
        """See IWeblogView.
        """
        return IWeblogConfiguration(self.context.getWeblogContentObject())

    def getWeblogEntriesDates(self, entries_dict):
        """See IWeblogView.
        """
        days = entries_dict.keys()
        days.sort()
        days.reverse()
        return days

    def sortWeblogEntriesToDates(self, lazy_entries, resolution='day'):
        """See IWeblogView.
        """
        if resolution == 'day':
            format = '%Y-%m-%d 00:00:00'
        elif resolution == 'month':
            format = '%Y-%m'
        elif resolution == 'year':
            format = '%Y'
        else:
            msg = "The 'resolution' parameter must be one of 'day', 'month', or 'year'.  You passed %s."
            raise Exception(msg % resolution)
        if isinstance(lazy_entries, PloneBatch):
            start = lazy_entries.start - 1
            end = lazy_entries.end
            lazy_entries = lazy_entries._sequence[start:end]
        results = {}
        for lazy_entry in lazy_entries:
            date = lazy_entry.effective.strftime(format)
            try:
                if results[date]:
                    # Add the entry to the top of the list for that day
                    results[date].append(lazy_entry)
            except:
                results[date] = [lazy_entry,]
        return results


class WeblogEntryView(BaseView):
    """
    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IWeblogEntryView, WeblogEntryView)
    True
    """

    implements(IWeblogEntryView)

    def getConfig(self):
        """See IWeblogView.
        """
        weblog = self.context.getWeblogContentObject()
        return IWeblogConfiguration(weblog)
    
    def workflow_state(self):
        """returns the current workflow state of the context"""
        wftool = getToolByName(self.context, 'portal_workflow')
        return wftool.getInfoFor(self.context, "review_state")


class TopicView(WeblogView):
    """
    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(ITopicView, TopicView)
    True
    """

    implements(ITopicView)

    def getLastModified(self):
        """See ITopicView.
        """
        entries = self.context.getEntries()
        if entries:
            # XXX modified should be in an interface
            return entries[0].modified


class WeblogArchiveView(BaseView):
    """A class with helper methods for use in views/templates.
    """

    #implements(IWeblogArchiveView)
    pass
