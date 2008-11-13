# Zope imports
from zope.formlib import form
from zope.interface import implements
from AccessControl import getSecurityManager
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

# CMF imports
from Products.CMFCore.permissions import AddPortalContent

# Plone imports
from plone.app.portlets.portlets import base
from plone.app.portlets.browser.formhelper import NullAddForm
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider

# Quills imports
from quills.core.interfaces import IWeblogLocator
from quills.app.interfaces import IWeblogEnhancedConfiguration
from quills.app import QuillsAppMessageFactory as _

# Local imports
from base import BasePortletRenderer


PORTLET_TITLE = _(u"Weblog Admin")
PORTLET_DESC = _(u"This portlet provides useful admin functions for a weblog.")


class IWeblogAdminPortlet(IPortletDataProvider):
    """A weblog administration portlet.
    """


class Assignment(base.Assignment):
    implements(IWeblogAdminPortlet)

    @property
    def title(self):
        return PORTLET_TITLE


class Renderer(BasePortletRenderer, base.Renderer):

    _template = ViewPageTemplateFile('weblogadmin.pt')

    @property
    def available(self):
        # This admin portlet is only available to people with the
        # 'Add portal content' permission.
        user = getSecurityManager().getUser()
        # I think has_permission sometimes returns 1 or None, so make sure that
        # we return True/False.
        if user.has_permission(AddPortalContent, self.context.aq_inner):
            # XXX Before returning True, we should also check the
            # BasePortletRenderer.available implementation. Not sure how to do
            # that as it's been property-ized on the base class.
            #return True
            return super(Renderer, self).available
        return False

    @property
    def title(self):
        return PORTLET_TITLE

    @property
    def add_entry_url(self):
        weblog_content = self.getWeblogContentObject()
        try:
            config = IWeblogEnhancedConfiguration(weblog_content)
            type_name = config.default_type
        except TypeError: # Could not adapt, so fall back to default.
            type_name = 'WeblogEntry'
        url = "%s/createObject?type_name=%s"
        return url % (weblog_content.absolute_url(), type_name)

    @property
    def drafts_url(self):
        weblog_content = self.getWeblogContentObject()
        return "%s/drafts/" % weblog_content.absolute_url()

    @property
    def manage_comments_url(self):
        weblog_content = self.getWeblogContentObject()
        return "%s/manage_comments" % weblog_content.absolute_url()

    @property
    def config_view_url(self):
        weblog_content = self.getWeblogContentObject()
        return "%s/config_view" % weblog_content.absolute_url()


class AddForm(NullAddForm):
    form_fields = form.Fields(IWeblogAdminPortlet)
    label = _(u'add-portlet', default=u"Add ${portlet-name} Portlet", mapping={u'portlet-name': PORTLET_TITLE})
    description = PORTLET_DESC

    def create(self):
        return Assignment()


class EditForm(base.EditForm):
    form_fields = form.Fields(IWeblogAdminPortlet)
    label = _(u'edit-portlet', default=u"Edit ${portlet-name} Portlet", mapping={u'portlet-name': PORTLET_TITLE})
    description = PORTLET_DESC
