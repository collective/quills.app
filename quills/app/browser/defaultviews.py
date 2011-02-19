# Zope imports
from zope.interface import implements
from zope.publisher.interfaces.browser import IBrowserPublisher


class DefaultView(object):
    """Provides the name of a default view. Abstract, subclasses
    must provide the name.
    
    Used by the Zope publisher during traversal.
    """
    implements(IBrowserPublisher)
    
    def __init__(self, name, context, request):
	self.name = name
	self.context = context
	self.request = request

    def publishTraverse(self, request, name):
        """See zope.publisher.interfaces.IPublishTraverse
        
        This is not really needed as browserDefault returns our
        context and not ourselves. 
        """
        return self.context.publishTraverse(request, name)

    def browserDefault(self, request):
        """See  zope.publisher.interfaces.IBrowserPublisher"""
        return (self.context, (self.name,))

class DefaultArchiveView(DefaultView):
    """Provide the name of the archive default view.
    """
    def __init__(self, context, request):
        super(DefaultArchiveView, self).__init__("@@archive_view",
                                                context, request)

class DefaultTopicsView(DefaultView):
    """Provide the name of the topic listing's default view.
    """
    def __init__(self, context, request):
        super(DefaultTopicsView, self).__init__("@@topic_listing",
                                                context, request)

class DefaultAuthorsView(DefaultView):
    """Provide the name of the authors listing's default view.
    """
    def __init__(self, context, request):
        super(DefaultAuthorsView, self).__init__("@@author_listing",
                                                context, request)
