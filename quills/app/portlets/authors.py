from zope import schema
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize.compress import xhtml_compress
from plone.portlets.interfaces import IPortletDataProvider

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from plone.memoize.instance import memoize

# Quills imports
from quills.core.interfaces import IWeblogLocator

PORTLET_TITLE = u"Weblog Authors"
PORTLET_DESC = u"This portlet lists weblog authors."


class IWeblogAuthorsPortlet(IPortletDataProvider):

    show_location = schema.Bool(
        title=_(u'Show author location?'),
        description=_(u"If available, should the author's location be shown?"),
        required=True,
        default=True)

    show_portrait = schema.Bool(
        title=_(u'Show author portrait?'),
        description=_(u"If available, should the author's portrait be shown?"),
        required=True,
        default=True)

    show_description = schema.Bool(
        title=_(u'Show author description?'),
        description=_(u"If available, should the author's description be shown?"),
        required=True,
        default=True)


class Assignment(base.Assignment):

    implements(IWeblogAuthorsPortlet)

    def __init__(self,
                 show_location=True,
                 show_portrait=True,
                 show_description=True):
        self.show_location = show_location
        self.show_portrait = show_portrait
        self.show_description = show_description

    @property
    def title(self):
        return _(PORTLET_TITLE)


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('authors.pt')

    #@ram.cache(render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return True

    @property
    def title(self):
        return _(PORTLET_TITLE)
    
    @memoize
    def getWeblogContent(self):
        locator = IWeblogLocator(self.context)
        weblog = locator.find()
        return weblog
    
    @property
    def authors(self):
        weblog = self.getWeblogContent()
        return weblog.getAuthors()

    def getPortraitFor(self, author):
        mtool = getToolByName(self.context, 'portal_membership')
        return mtool.getPersonalPortrait(author.getId())

    def getInfoFor(self, author):
        mtool = getToolByName(self.context, 'portal_membership')
        info = mtool.getMemberInfo(author.getId())
        if info is None:
            info = { 'fullname'    : author.getId(),
                     'description' : '',
                     'location'    : '',
                     'language'    : '',
                     'home_page'   : '',
                     'username'    : author.getId(),
                   }
        if not info['fullname']:
            info['fullname'] = author.getId()
        if not info['username']:
            info['username'] = author.getId()
        return info
    
    def getAuthorURL(self, author_id):
        weblog = self.getWeblogContent()
        return "%s/authors/%s" % (weblog.absolute_url(), author_id)
    
    def getAuthorsURL(self):
        weblog = self.getWeblogContent()
        return "%s/authors" % weblog.absolute_url()


class AddForm(base.AddForm):
    form_fields = form.Fields(IWeblogAuthorsPortlet)
    label = _(u"Add %s Portlet" % PORTLET_TITLE)
    description = _(PORTLET_DESC)

    def create(self, data):
        return Assignment(show_location=True,
                          show_portrait=True,
                          show_description=True)


class EditForm(base.EditForm):
    form_fields = form.Fields(IWeblogAuthorsPortlet)
    label = _(u"Edit %s Portlet" % PORTLET_TITLE)
    description = _(PORTLET_DESC)
