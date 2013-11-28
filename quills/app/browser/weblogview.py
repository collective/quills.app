# Zope imports
from zope.interface import implements

# Plone imports
from Products.CMFPlone.PloneBatch import Batch as PloneBatch
from Products.CMFCore.utils import getToolByName
from plone.app.layout.globals.interfaces import IViewView
from plone.app.layout.viewlets.common import TitleViewlet as BaseTitleViewlet

# Quills imports
from quills.core.interfaces import IWeblog
from quills.core.interfaces import IWeblogEntry
from quills.core.browser.interfaces import IWeblogView
from quills.core.browser.interfaces import IWeblogEntryView
from quills.core.browser.interfaces import ITopicView
from baseview import BaseView
from quills.app.interfaces import IWeblogEnhancedConfiguration
from quills.core.interfaces import IWeblogLocator
from quills.app import QuillsAppMessageFactory as _

try:
    from Products.CMFPlone.utils import translate
except ImportError:
    translate = None


class WeblogView(BaseView):
    """A class with helper methods for use in views/templates.

    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IWeblogView, WeblogView)
    True
    """

    implements(IWeblogView)

    def getWeblog(self):
        return IWeblog(self.context)

    def getWeblogContentObject(self):
        return self.context

    def getConfig(self):
        """See IWeblogView.
        """
        return IWeblogEnhancedConfiguration(self.getWeblogContentObject())

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
            format = '%Y/%m/%d 00:00:00'
        elif resolution == 'month':
            format = '%Y-%m'
        elif resolution == 'year':
            format = '%Y'
        else:
            msg = "The 'resolution' parameter must be one of 'day', 'month', \
                   or 'year'.  You passed %s."
            raise Exception(msg % resolution)
        if isinstance(lazy_entries, PloneBatch):
            start = lazy_entries.start - 1
            end = lazy_entries.end
            lazy_entries = lazy_entries._sequence[start:end]
        results = {}
        for lazy_entry in lazy_entries:
            date = lazy_entry.getPublicationDate().strftime(format)
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

    implements(IWeblogEntryView, IViewView)

    def getWeblog(self):
        return self.getWeblogEntry().getWeblog()

    def getWeblogContentObject(self):
        return IWeblogEntry(self.context).getWeblogContentObject()

    def getWeblogEntry(self):
        return IWeblogEntry(self.context)

    def getConfig(self):
        """See IWeblogView.
        """
        weblog = self.getWeblogContentObject()
        return IWeblogEnhancedConfiguration(weblog)
    
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

    def getWeblog(self):
        """Return the weblog object.
        """
        locator = IWeblogLocator(self.context)
        return locator.find()

    def getWeblogContentObject(self):
        """ Return the content object underlying the weblog object,
        or the weblog object itself, if there is no such object.
        """
        weblog = self.getWeblog()
        return getattr(weblog, 'context', weblog)

    def getConfig(self):
        """See IWeblogView.
        """
        return IWeblogEnhancedConfiguration(self.getWeblogContentObject())

    def getLastModified(self, topic=None):
        """See ITopicView.
        """
        if topic is None:
            topic = self.context
        entries = topic.getEntries()
        if entries:
            # XXX modified should be in an interface
            return entries[0].modified

    def topicViewURLof(self, topic):
        """Return the URL of the view for given topic."""
        if self.viewContainerName():
            return '%s/%s/%s' % (self.getWeblogContentObject().absolute_url(),
                                 self.viewContainerName(),
                                 topic.getId())
        else:
            return '%s/%s' % (self.getWeblogContentObject().absolute_url(),
                                 topic.getId())            

    def viewContainerName(self):
        """Return the vitual container name that can be appended to the
        weblog url for browsing topics of a certain kind.
        """
        raise AttributeError("Sub-class responsibility")


class KeywordTopicView(TopicView):
    """A view for keyword topics."""

    def viewContainerName(self):
        """See base-class."""
        return "topics"


class AuthorTopicView(TopicView):
    """A view for author topics."""

    def viewContainerName(self):
        """See base-class."""
        return "authors"
    
class WeblogArchiveView(TopicView):
    """A class with helper methods for use in views/templates.
    """

    #implements(IWeblogArchiveView)
    pass


class TopicTitleViewlet(BaseTitleViewlet):
    """Render the title attribute of the HTML head in a meaningful and
    bookmark-friendly way. This one is for ITopic (keyword) content.
    """
    
    def update(self):
        """Customize plone.app.layout.viewlets.common.TitleViewlet. Look there
        for what goes on here."""
        context = self.context
        def blog_title():
            return context.getWeblog().getTitle()
        def post_title():
            message = _(u'posts_by_keywords', default=u'Posts about $keywords',
                        mapping={'keywords':context.getTitle()})
            if translate:
                ## Plone 4
                return translate(message)
            
            ## for Plone 3
            return context.translate(message)
         
        #BBB
        self.portal_title = blog_title
        #self.page_title = post_title        # does not work in Plone 4.3
        ## Plone 4
        self.site_title = blog_title

class AuthorTopicTitleViewlet(BaseTitleViewlet):
    """Render the title attribute of the HTML head in a meaningful and
    bookmark-friendly way. This one is for IAuthorTopic content.
    """
    
    def update(self):
        """Customize plone.app.layout.viewlets.common.TitleViewlet. Look there
        for what goes on here."""
        context = self.context
        def blog_title():
            return context.getWeblog().getTitle()
        def post_title():
            message = _(u'posts_by_authors', default=u'Posts by $authors',
                        mapping={'authors':context.getTitle()})
            if translate:
                ## Plone 4
                return translate(message)
            
            ## for Plone 3
            return context.translate(message)
        
        ##BBB
        self.portal_title = blog_title
        #self.page_title = post_title   # does not work in Plone 4.3
        ## Plone 4
        self.site_title = blog_title
