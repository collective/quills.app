# Plone imports
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize

# Quills imports
from quills.core.interfaces import IWeblogLocator


class BasePortletRenderer:

    #@ram.cache(render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return self.getWeblog() != [] and True or False

    @memoize
    def getWeblog(self):
        locator = IWeblogLocator(self.context)
        weblog = locator.find()
        return weblog

    @memoize
    def getWeblogContentObject(self):
        weblog = self.getWeblog()
        if getattr(weblog, 'absolute_url', None):
            return weblog
        elif getattr(weblog, 'context', None):
            # `weblog' is presumably an adapter around the real content object.
            return weblog.context
