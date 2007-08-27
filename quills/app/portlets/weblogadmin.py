from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize import ram
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.cache import render_cachekey

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _


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

    @ram.cache(render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return True


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
