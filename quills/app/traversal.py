from Acquisition import aq_base
from ZPublisher.BaseRequest import DefaultPublishTraverse
from archive import ArchiveContainer
from archive import DayArchive
from archive import MonthArchive
from archive import YearArchive
from quills.core.interfaces import IAuthorContainer
from quills.core.interfaces import ITopicContainer
from quills.core.interfaces import IWeblog
from quills.core.interfaces import IWeblogArchive
from quills.core.interfaces import IWeblogConfiguration
from topic import AuthorContainer
from topic import AuthorTopic
from topic import Topic
from topic import TopicContainer
from zope.component import adapts, getMultiAdapter
from zope.interface import alsoProvides
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.publisher.interfaces.http import IHTTPRequest

try:
    from zope.app.publisher.browser import getDefaultViewName
except ImportError:
    from zope.publisher.defaultview import getDefaultViewName


class IInsideWeblog(IDefaultBrowserLayer):
    """Marker interface for Requests to signal that traversal moves
    inside a QuillsEnabled weblog. To trigger a view or a browser page
    only for content inside a weblog simply set this interface as the layer
    of the view/page.  
    """


class WeblogTraverser(DefaultPublishTraverse):
    """ """
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
    """ """
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

        year = getattr(aq_base(self.context), 'year', None)
        month = getattr(aq_base(self.context), 'month', None)
        day = getattr(aq_base(self.context), 'day', None)
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

    def publishTraverse(self, request, name):
        """Interpret any remaining names on the traversal stack as keywords
        of this topic container. Only exception is an appended view name at
        the end of the traversal stack, or if a sub-class aborts the process

        This operation will empty the traversal stack! While the view have
        an instance of ``klass`` as context, it will have the topic container
        as acquistion parent! The ``klass`` instance will be initialized with
        the keywords taken from the traversal stack.
        """
        self.request = request

        # collect keywords
        keywords = []
        while self.hasMoreNames():
            keywords.append(name)
            name = self.nextName()

        # Determine view
        view_name = None
        context = None
        if name.startswith('@@'): 
            # A view has explicitly been requested, so make that the 
            # view_name (stripping off the leading @@ which causes view 
            # lookups to fail otherwise). 
            view_name = name[2:]
        else:
            # last name is another keyword
            keywords.append(name)

        if len(keywords) == 0:
            # No keywords given, just a view specified. Create a view for the
            # topic container.
            context = self.context
        else:
            context = self.wrapUp(keywords).__of__(self.context)

        view_name = view_name or getDefaultViewName(context, request)
        view = getMultiAdapter((context, request), name=view_name) 
        return view.__of__(self.context) 

    def nextName(self): 
        """Pop the next name off of the traversal stack.
        """
        return self.request['TraversalRequestNameStack'].pop() 

    def hasMoreNames(self):
        """Are there names left for traversal?
        """
        return len(self.request['TraversalRequestNameStack']) > 0

    def wrapUp(self, keywords): 
        """Create a content object for the given keywords. 
         """ 
        raise NotImplementedError("subclass responsibility") 


class TopicContainerTraverser(BaseContainerTraverser):
    """Topic container traversal
    
    blog/topics/topic_name
    """
    adapts(ITopicContainer, IHTTPRequest)

    def wrapUp(self, keywords): 
        """See super-class.""" 
        return Topic(keywords)


class AuthorContainerTraverser(BaseContainerTraverser):
    """Author container traversal
    
    blog/authors/author_id
    """
    adapts(IAuthorContainer, IHTTPRequest)

    def wrapUp(self, keywords): 
        """See super-class.""" 
        return AuthorTopic(keywords)

            
