# Zope imports
from zope.component import adapts, getMultiAdapter
from zope.component import queryMultiAdapter
from zope.app.publisher.browser import getDefaultViewName
from zope.interface import alsoProvides, Interface
from zope.publisher.interfaces.http import IHTTPRequest
from ZPublisher.BaseRequest import DefaultPublishTraverse
from Products.CMFCore.utils import getToolByName

# Quills imports
from quills.core.interfaces import IWeblog
from quills.core.interfaces import IWeblogEntry
from quills.core.interfaces import IWeblogArchive
from quills.core.interfaces import IWeblogConfiguration
from quills.core.interfaces import IPossibleWeblogEntry
from quills.core.interfaces import ITopicContainer
from quills.core.interfaces import IAuthorContainer

# Local imports
from topic import Topic
from topic import AuthorTopic
from topic import TopicContainer
from topic import AuthorContainer
from archive import ArchiveContainer
from archive import YearArchive
from archive import MonthArchive
from archive import DayArchive

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
class IInsideWeblog(IDefaultBrowserLayer):
    """Marker interface for Requests to signal that traversal moves
    inside a QuillsEnabled weblog. To trigger a view or a browser page
    only for content inside a weblog simply set this interface as the layer
    of the view/page.  
    """


class WeblogTraverser(DefaultPublishTraverse):

    adapts(IWeblog, IHTTPRequest)
    
    def publishTraverse(self, request, name):
        # Mark request: we're in a weblog
        # You can trigger views/pages by using layer "IInsideWeblog" now.
        alsoProvides(request, IInsideWeblog)

        # Only intercept certain names...
        if name == 'topics':
            # XXX 'topics' should probably not be hard-coded here.  Rather,
            # it should be looked up on weblog config.
            return TopicContainer('topics').__of__(self.context)
        elif name == 'authors':
            # XXX 'authors' should probably not be hard-coded here.  Rather,
            # it should be looked up on weblog config.
            return AuthorContainer('authors').__of__(self.context)
        elif self.isArchiveFolder(name):
            return ArchiveContainer(name).__of__(self.context)
        elif self.isYear(name):
            return YearArchive(name).__of__(self.context)
        return super(WeblogTraverser, self).publishTraverse(request, name)

    def isArchiveFolder(self, name):
        """Test if 'name' is an archive folder.  This is True when name is the
        value indicated by weblog_config
        """
        weblog_config = IWeblogConfiguration(self.context)
        if name == weblog_config.archive_format:
            return True
        return False

    def isYear(self, name):
        try:
            year = int(name)
        except ValueError:
            return False
        else:
            from DateTime import DateTime
            try:
                tryDate = DateTime(year,1,1)
            except:
                # Bad year
                return False
            else:
                return True


class WeblogArchiveTraverser(DefaultPublishTraverse):
    """
    """

    adapts(IWeblogArchive, IHTTPRequest)

    def publishTraverse(self, request, name):
        """
        """
        isdate = False
        try:
            int(name)
            isdate = True
        except ValueError:
            pass
        if not isdate:
            # We're at the end of the archive hierarchy, and now need to
            # traverse for the actual IWeblogEntry item.  The trick here is to
            # lookup the weblogentry-ish view on an object that is an
            # IPossibleWeblogEntry so that it gets rendered in the weblog-ish
            # way.
            # So, we do standard traversal to get the actual object.
            obj = super(WeblogArchiveTraverser,
                        self).publishTraverse(request, name)
            return obj

        year = getattr(self.context, 'year', None)
        month = getattr(self.context, 'month', None)
        day = getattr(self.context, 'day', None)
        if day is not None:
            return super(WeblogArchiveTraverser,
                         self).publishTraverse(request, name)
        if month is not None:
            archive = DayArchive(year, month, name)
        elif year is not None:
            archive = MonthArchive(year, name)
        else:
            archive = YearArchive(name)
        ob = archive.__of__(self.context)
        return ob


class BaseContainerTraverser(DefaultPublishTraverse):
    """Base traverser for Topics and Authors
    """

    def traverseSubpath(self, request, name, klass):
        """ Answer an instance of ``klass`` as object at ``name``. Merge
        keywords of the parent object (i.e. of the context) into
        that object, if the parent happens to be of the same ``klass``.
        """
        # Is this a  multi-keyword query, i.e. have?
        if isinstance(self.context, klass):
            # Yes, augment the keywords of our parent
            topics = self.context.getKeywords() + [name]
        else:
            topics = [name]
        return klass(topics).__of__(self.context)

class TopicContainerTraverser(BaseContainerTraverser):
    """Topic container traversal
    
    blog/topics/topic_name
    """

    # It actually adapts ITopics too, now...
    adapts(ITopicContainer, IHTTPRequest)

    def publishTraverse(self, request, name):
        """Accept any name unless an object by that name can be found by
        the DefaultPublishTraverse. In that case return this object unless
        there exists a blog post by that topic (keyword) in the blog.

        This somewhat complicated rule shall minimize the cases where a 
        required object from the context (e.g. an image) is hidden by a
        keyword never actually used by the blog.
        """
        try:
            obj = super(TopicContainerTraverser,
                        self).publishTraverse(request, name)
        except AttributeError: 
            return self.traverseSubpath(request, name, Topic)
        # This next two statement might look quite heavy-weight, after all
        # they cause a catalog query, amongst other. However, this
        # code is only executed when object ids clash. That should
        # happen fairly seldom.
        # XXX Issue a warning to the user when names clash!
        # --- jhackel
        weblog = self.context.getWeblog()
        if len(weblog.getTopicById(name).getEntries()) == 0:
            return obj
        else:
            return self.traverseSubpath(request, name, Topic)

class AuthorContainerTraverser(BaseContainerTraverser):
    """Author container traversal
    
    blog/authors/author_id
    """

    # It actually adapts IAuthorTopics too, now...  
    adapts(IAuthorContainer, IHTTPRequest)
    
    def publishTraverse(self, request, name):
        """Create a Topic for any name that denotes a portal member.
        Being an actual author of the blog is not required though.
        """
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.getMemberById(name) is None:
            return super(AuthorContainerTraverser,
                         self).publishTraverse(request, name)
        else:
            return self.traverseSubpath(request, name, AuthorTopic)
            
