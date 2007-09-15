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



PORTLET_TITLE = u"Tag Cloud"
PORTLET_DESC = u"This portlet displays a tag cloud."


class ITagCloudPortlet(IPortletDataProvider):
    """A tag cloud portlet.
    """


class Assignment(base.Assignment):

    implements(ITagCloudPortlet)

    @property
    def title(self):
        return _(PORTLET_TITLE)


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('tagcloud.pt')

    #@ram.cache(render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return True

    @property
    def title(self):
        return _(PORTLET_TITLE)

    def getCloud(self):
        weblog_content = recurseToInterface(self.context.aq_inner,
                                            (IWeblog, IWeblogEnhanced))
        weblog = IWeblog(weblog_content)
        # Get a list of topics, sorted alphabetically
        topics = weblog.getTopics()
        if not topics:
            return []
        # Create a list of entries for each topic
        topic_size = []
        for topic in topics:
            topic_size.append(len(topic))
        # Find the Min and Max number entries
        min_topic_size = min(topic_size)
        max_topic_size = max(topic_size)
        # Make sure size_topic_size is never 0, or we get ZeroDivisionError later
        size_topic_size = max_topic_size - min_topic_size + 0.0 or 1
        # Create a list to return tuples containing the:
        #    - topic object
        #    - relative weight of the topic, 0.0 to 1.0
        #    - number of entries for that topic, since we already calculated it.
        # Skip topics that have no entries.
        result = []
        for topic, number_of_entries in zip(topics, topic_size):
            if number_of_entries > 0:
                # Normalize the result
                rel = ( (number_of_entries - min_topic_size ) / size_topic_size )
                # Add the result
                cloud_dict = {'topic'               :   topic,
                              'rank'                :   rel,
                              'size'                :   int(rel*10),
                              'number_of_entries'   :   number_of_entries}
                result.append(cloud_dict)
        # Done...
        return result


class AddForm(base.AddForm):
    form_fields = form.Fields(ITagCloudPortlet)
    label = _(u"Add Tag Cloud Portlet")
    description = _(PORTLET_DESC)

    def create(self, data):
        return Assignment()


class EditForm(base.EditForm):
    form_fields = form.Fields(ITagCloudPortlet)
    label = _(u"Edit %s Portlet" % PORTLET_TITLE)
    description = _(PORTLET_DESC)
