# Zope imports
from zope.component import adapts, getMultiAdapter
from zope.component import queryMultiAdapter
from zope.app.publisher.browser import getDefaultViewName
from zope.interface import alsoProvides, Interface
from zope.publisher.interfaces.http import IHTTPRequest
from ZPublisher.BaseRequest import DefaultPublishTraverse
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_base

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

     Why not cosume all keywords here?
   
        - the name might in fact designate a required content object,
          e.g an image (issue #???)
       
        - the last component might be a view name. Not all view names can
          easily be resolve by publishTraverse, some require bobo_traverse
          or other dark magic. We leave that better to the Zope publisher.
          (See test-cases for issue #???)

    Why not let Topic act as content objects that have specialized views?
       
        - I tried that. I works until a keyword contains non-ascii characters.
          Zope (or rather urllib) will choke on them. (Issue #???)

    But formerly Topics worked that way!

        - Yes but it required black magic, too. The topic view would have
          the topic as context but would be acquisition chained to the 
          topic container, thus avoiding unicode issues. This however
          cannot easily be replicated when names are looked up one by one.
          In fact what we do now -- temporarily storing the know keywords
          in the request -- tries to do that trick.
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
        preferredObject = self.disambiguate(name)
        if not preferredObject is None:
           return preferredObject     
        elif self.moreNames():
            self.keywords().append(name)
            return self.context           
        else:
            keywords = self.keywords()
            keywords.append(name)
            return self.wrapUp(keywords).__of__(self.context)

    def defaultPublishTraverse(self, request, name):
        """Convenient access to C{DefaultPublishTraverse.publishTraverse}.
        """
        return super(BaseContainerTraverser, 
                     self).publishTraverse(request, name)

    def disambiguate(self, request, name):
        """Check whether the given name shall be treated as a keyword of the
        topic container (i.e. some sort of query string), or whether it
        designates a content object (e.g. an image) that should precedence
        before queries.

        Implementations may consult the request via C{self.request}.

        This mechanism responds to issue #198, where images with posts would
        disappear when displayed by the topic or author view, because
        Quills would serve another topic view (HTML) instead of the image.

        @return C{None} if no content object shall override the give name.
            Return the content object otherwise. It will be left untouched
            by the caller (C{publishTraverse}), so make sure it is properly
            acquisition chained!
        """
        raise NotImplementedError("subclass responsibility")

    def wrapUp(self, keywords):
        """Create a content object for the given keywords.
         """
        raise NotImplementedError("subclass responsibility")

    def keywords(self):
        """Return the keywords see sofar during this publishing cycle, or
        an empty list if none has been read yet. Modifications to this
        list will survive until publication is finnished.
        """
        if not 'quills.traversal.topics' in self.request:
            self.request['quills.traversal.topics'] = []
        return self.request['quills.traversal.topics']

    def moreNames(self):
        """Are there more names to be processed by traversal, i.e. is
        the traversal stack not empty?
        """
        return len(self.request['TraversalRequestNameStack']) > 0

class TopicContainerTraverser(BaseContainerTraverser):
    """Topic container traversal
    
    blog/topics/topic_name
    """

    adapts(ITopicContainer, IHTTPRequest)

    def wrapUp(self, keywords):
        """See super-class."""
        return Topic(keywords)

    def disambiguate(self, name):
        """Accept any name unless an object by that name can be found by
        the DefaultPublishTraverse. In that case return this object unless
        there exists a blog post by that topic (keyword) in the blog.

        This somewhat complicated rule shall minimize the cases where a 
        required object from the context (e.g. an image) is hidden by a
        keyword never actually used by the blog.
        """
        try:
            obj = super(BaseContainerTraverser,
                        self).publishTraverse(self.request, name)
        except AttributeError: 
            return None
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
            return None

    def OldpublishTraverse(self, request, name):
        """Accept any name unless an object by that name can be found by
        the DefaultPublishTraverse. In that case return this object unless
        there exists a blog post by that topic (keyword) in the blog.

        This somewhat complicated rule shall minimize the cases where a 
        required object from the context (e.g. an image) is hidden by a
        keyword never actually used by the blog.
        """
        try:
            # We refer to DefaultPublishTraverse.publishTraverse here!
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

    adapts(IAuthorContainer, IHTTPRequest)

    def wrapUp(self, keywords):
        """See super-class."""
        return AuthorTopic(keywords)

    def disambiguate(self, name):
        """Accept any name that denotes a portal member. Being an actual
        author of the blog is not required though.
        """
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.getMemberById(name) is None:
            # We refer to DefaultPublishTraverse.publishTraverse here!
            return super(BaseContainerTraverser,
                         self).publishTraverse(self.request, name)
        else:
            return None
    
    def oldPublishTraverse(self, request, name):
        """Create a Topic for any name that denotes a portal member.
        Being an actual author of the blog is not required though.
        """
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.getMemberById(name) is None:
            return super(AuthorContainerTraverser,
                         self).publishTraverse(request, name)
        else:
            return self.traverseSubpath(request, name, AuthorTopic)
            
