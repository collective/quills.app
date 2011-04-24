# Zope imports
from zope.interface import implements
from zope.formlib import form

# plone imports
from Products.statusmessages.interfaces import IStatusMessage
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

# Quills imports
from quills.core.browser.weblogconfig import WeblogConfigAnnotations
from quills.core.browser.weblogconfig import WeblogConfigEditForm
from quills.app.interfaces import IStateAwareWeblogConfiguration
from quills.app.interfaces import IWeblogEnhancedConfiguration
from quills.app import QuillsAppMessageFactory as _

class StateAwareWeblogConfig(WeblogConfigAnnotations):
    """
    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IWeblogEnhancedConfiguration, StateAwareWeblogConfig)
    True
    """

    implements(IWeblogEnhancedConfiguration)

    default_type = "WeblogEntry"

    def _get_published_states(self):
        return self._config.get('published_states', ['published',])
    def _set_published_states(self, value):
        self._config['published_states'] = value
    published_states = property(_get_published_states, _set_published_states)

    def _get_draft_states(self):
        return self._config.get('draft_states', ['private',])
    def _set_draft_states(self, value):
        self._config['draft_states'] = value
    draft_states = property(_get_draft_states, _set_draft_states)


class StateAwareWeblogConfigEditForm(WeblogConfigEditForm):
    """Edit form for weblog view configuration.
    """
    label = _(u'Configure Blog')
    description = _(u"Weblog View Configuration")
    form_name = _(u"Configure rule")
    template = ViewPageTemplateFile('weblogconfig.pt')

    # We use IStateAwareWeblogConfiguration instead of
    # IWeblogEnhancedConfiguration because we don't want to generate form
    # input for the default_type field.
    form_fields = form.Fields(IStateAwareWeblogConfiguration)


    def setUpWidgets(self, ignore_request=False):
        self.adapters = {}
        wvconfig = IStateAwareWeblogConfiguration(self.context)
        self.widgets = form.setUpEditWidgets(
            self.form_fields, self.prefix, wvconfig, self.request,
            adapters=self.adapters, ignore_request=ignore_request
            )

    @form.action("submit")
    def submit(self, action, data):
        """ """
        wvconfig = IStateAwareWeblogConfiguration(self.context)
        form.applyChanges(wvconfig, self.form_fields, data)
        msg = _(u'Configuration saved.')
        IStatusMessage(self.request).addStatusMessage(msg, type='info')

