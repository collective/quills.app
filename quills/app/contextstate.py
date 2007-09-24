# Zope imports
from zope.app.publisher.browser import getDefaultViewName

# Plone imports
from plone.app.layout.globals.context import ContextState

# Quills imports
from quills.core.interfaces import IWeblogEntry


class QuillsContextState(ContextState):
    """A custom view component that knows how to answer is_view_template for
    Quills objects.
    """

    def is_view_template(self):
        # We only do something special for IWeblogEntry objects.
        #if not IWeblogEntry.providedBy(self.context):
        #    return super(QuillsContextState, self).is_view_template()
        url = self.current_base_url()
        url_parts = url.split('/')
        if url_parts[-1] == self.context.getId():
            # The last part of the URL is the same as the id of the object, so
            # we assume that there is no extra view specified, and thus that we
            # must be on the default view of the object.
            return True
        elif url_parts[-1] == getDefaultViewName(self.context, self.request):
            # The last part of the URL is the same as the default view name, so
            # we assume that we are using the default view.
            return True
        return False
