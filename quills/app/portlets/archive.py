from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize.compress import xhtml_compress
from plone.portlets.interfaces import IPortletDataProvider

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _

# Quills imports
from quills.core.interfaces import IWeblogEnhanced
from quills.core.interfaces import IWeblog
from quills.app.utilities import recurseToInterface
from quills.app.browser.baseview import BaseView


PORTLET_TITLE = u"Weblog Archive"
PORTLET_DESC = u"This portlet lists the archive of this weblog."


class IWeblogArchivePortlet(IPortletDataProvider):
    """a portlet showing the archive of the current weblog"""


class Assignment(base.Assignment):

    implements(IWeblogArchivePortlet)

    @property
    def title(self):
        return _(PORTLET_TITLE)


class Renderer(base.Renderer, BaseView):

    _template = ViewPageTemplateFile('archive.pt')

    #@ram.cache(render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return True

    @property
    def title(self):
        return _(PORTLET_TITLE)

    @property
    def getSubArchives(self):
        weblog_content = recurseToInterface(self.context.aq_inner,
                                           (IWeblog, IWeblogEnhanced))
        return weblog_content.getArchives().getSubArchives()

class AddForm(base.AddForm):
    form_fields = form.Fields(IWeblogArchivePortlet)
    label = _(u"Add %s Portlet" % PORTLET_TITLE)
    description = _(PORTLET_DESC)

    def create(self, data):
        return Assignment()


class EditForm(base.EditForm):
    form_fields = form.Fields(IWeblogArchivePortlet)
    label = _(u"Edit %s Portlet" % PORTLET_TITLE)
    description = _(PORTLET_DESC)
