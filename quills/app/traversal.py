# Zope imports
from zope.interface import implements
from zope.component import adapts, getMultiAdapter, queryMultiAdapter
from zope.app.publisher.browser import getDefaultViewName
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.http import IHTTPRequest
from ZPublisher.BaseRequest import DefaultPublishTraverse

# Quills imports
from quills.core.interfaces import IWeblog, IWeblogArchive

# Local imports
from topic import Topic, AuthorTopic
from archive import ArchiveContainer, YearArchive, MonthArchive, DayArchive


# Archive names
ARCHIVE_NAMES = ['archive',]


class WeblogTraverser(DefaultPublishTraverse):

    adapts(IWeblog, IHTTPRequest)
    
    def __init__(self, context, request):
        self.subpath = []
        self.klass = None
        return super(WeblogTraverser, self).__init__(context, request)

    def publishTraverse(self, request, name):
        # Only intercept certain names...
        has_subpath = self.requestHasSubpath(request)
        if name == 'topics':
            if not has_subpath:
                return self.getViewOrTraverse(request, name)
            klass = Topic
            return self.traverseSubpath(request, name, klass)
        elif name == 'authors':
            if not has_subpath:
                return self.getViewOrTraverse(request, name)
            klass = AuthorTopic
            return self.traverseSubpath(request, name, klass)
        elif isArchiveFolder(name):
            return ArchiveContainer(name).__of__(self.context)
        else:
            return self.getViewOrTraverse(request, name)

    def getViewOrTraverse(self, request, name):
        view = queryMultiAdapter((self.context, request), name=name)
        if view is not None:
            return view.__of__(self.context)
        return super(WeblogTraverser, self).publishTraverse(request, name)

    def requestHasSubpath(self, request):
        furtherPath = request['TraversalRequestNameStack']
        if furtherPath:
            return True
        return False

    def traverseSubpath(self, request, name, klass):
        # Now the guts of it...
        furtherPath = request['TraversalRequestNameStack']
        # Empty furtherPath so no more traversal happens after us.
        subpath = self.popFurtherPath(furtherPath)
        view_name = name
        if len(subpath) == 0:
            # No subpath to eat, so just lookup the 'name' view for context
            view = getMultiAdapter((self.context, self.request), name=view_name)
            return view.__of__(self.context)
        elif len(subpath) > 0 and subpath[-1].startswith('@@'):
            # A view has explicitly been requested, so make that the
            # view_name (stripping off the leading @@ which causes view
            # lookups to fail otherwise).
            view_name = subpath[-1][2:]
            # Use the rest of the subpath as the keywords for the topic.
            topic = klass(subpath[:-1]).__of__(self.context)
            view = getMultiAdapter((topic, request), name=view_name)
            return view.__of__(self.context)
        else:
            # No @@view given, so just return the topic.
            # Use all of the subpath as the keywords for the topic.
            topic = klass(subpath).__of__(self.context)
            view_name = getDefaultViewName(topic, request)
            view = getMultiAdapter((topic, request), name=view_name)
            return view.__of__(self.context)

    def popFurtherPath(self, furtherPath):
        """Empty the furtherPath sequence into a new list.
        """
        # XXX This should probably do something (hacky?) to inform the request
        # of what the full URL is.  Otherwise, things like ACTUAL_URL will be
        # wrong.
        subpath = []
        subpath.extend(furtherPath)
        while furtherPath:
            furtherPath.pop()
        return subpath


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
            return super(WeblogArchiveTraverser, self).publishTraverse(request, name)
        year = getattr(self.context, 'year', None)
        month = getattr(self.context, 'month', None)
        day = getattr(self.context, 'day', None)
        if day is not None:
            return super(WeblogArchiveTraverser, self).publishTraverse(request, name)
        if month is not None:
            archive = DayArchive(year, month, name)
        elif year is not None:
            archive = MonthArchive(year, name)
        else:
            archive = YearArchive(name)
        ob = archive.__of__(self.context)
        return ob


def isArchiveFolder(name):
    """Test is 'name' is an archive folder.

    This is True when:
    - name == 'archive'
    - name is a year
    """
    if name == 'archive':
        return True
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