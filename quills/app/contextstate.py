from plone.app.layout.globals.context import ContextState
try:
    from zope.app.publisher.browser import getDefaultViewName
except ImportError:
    from zope.publisher.defaultview import getDefaultViewName


class QuillsContextState(ContextState):
    """A custom view component that knows how to answer is_view_template for
    Quills objects. This is needed for Plone to recognize view templates at
    virtual URLSs, like for instance archive URLs. Plone's default
    implementation bases it's decision only on the absolute object
    URL (which differs from the virtual URL) and thus always yields "False".
    See Quills issues #97 and #193 for the ill effects this could have.
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
