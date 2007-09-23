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
from quills.core.interfaces import IWeblogEnhancedConfiguration


PORTLET_TITLE = u"Weblog Admin"
PORTLET_DESC = u"This portlet provides useful admin functions for a weblog."

class IWeblogAdminPortlet(IPortletDataProvider):
    """A weblog administration portlet.
    """


class Assignment(base.Assignment):
    implements(IWeblogAdminPortlet)

    @property
    def title(self):
        return _(PORTLET_TITLE)


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('weblogadmin.pt')

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
    def add_entry_url(self):
        weblog_content = self._getWeblogContent()
        try:
            config = IWeblogEnhancedConfiguration(weblog_content)
            type_name = config.default_type
        except TypeError: # Could not adapt, so fall back to default.
            type_name = 'WeblogEntry'
        url = "%s/createObject?type_name=%s"
        return url % (weblog_content.absolute_url(), type_name)

    @property
    def drafts_url(self):
        weblog_content = self._getWeblogContent()
        return "%s/drafts/" % weblog_content.absolute_url()

    @property
    def manage_comments_url(self):
        weblog_content = self._getWeblogContent()
        return "%s/manage_comments" % weblog_content.absolute_url()

    @property
    def config_view_url(self):
        weblog_content = self._getWeblogContent()
        return "%s/config_view" % weblog_content.absolute_url()

    def _getWeblogContent(self):
        weblog_content = getattr(self, '_v_weblog_content', None)
        if weblog_content is None:
            weblog_content = recurseToInterface(self.context.aq_inner,
                                                (IWeblog, IWeblogEnhanced))
        return weblog_content


class AddForm(base.AddForm):
    form_fields = form.Fields(IWeblogAdminPortlet)
    label = _(u"Add %s Portlet" % PORTLET_TITLE)
    description = _(PORTLET_DESC)

    def create(self, data):
        return Assignment()


class EditForm(base.EditForm):
    form_fields = form.Fields(IWeblogAdminPortlet)
    label = _(u"Edit %s Portlet" % PORTLET_TITLE)
    description = _(PORTLET_DESC)
