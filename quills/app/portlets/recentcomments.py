from zope import schema
from zope.formlib import form
from zope.interface import implements
from zope.component import getMultiAdapter

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


PORTLET_TITLE = u"Recent Comments"
PORTLET_DESC = u"This portlet lists recent weblog comments."


class IRecentWeblogCommentsPortlet(IPortletDataProvider):

    max_comments = schema.Int(
        title=_(u'Maximum comments'),
        description=_(u"What's the maximum number of comments to list?"),
        required=True,
        default=5)


class Assignment(base.Assignment):

    implements(IRecentWeblogCommentsPortlet)

    def __init__(self, max_comments=5):
        self.max_comments = max_comments

    @property
    def title(self):
        return _(PORTLET_TITLE)


class Renderer(base.Renderer, BaseView):

    _template = ViewPageTemplateFile('recentcomments.pt')

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
    def getComments(self):
        weblog_content = recurseToInterface(self.context.aq_inner,
                                           (IWeblog, IWeblogEnhanced))
        weblog = IWeblog(weblog_content)
        view = getMultiAdapter((weblog, self.request), name='manage_comments')
        return view.getComments()[:self.data.max_comments]


class AddForm(base.AddForm):
    form_fields = form.Fields(IRecentWeblogCommentsPortlet)
    label = _(u"Add %s Portlet" % PORTLET_TITLE)
    description = _(PORTLET_DESC)

    def create(self, data):
        return Assignment(max_comments=5)


class EditForm(base.EditForm):
    form_fields = form.Fields(IRecentWeblogCommentsPortlet)
    label = _(u"Edit %s Portlet" % PORTLET_TITLE)
    description = _(PORTLET_DESC)
