"""Provide access to Quills' metal macros."""

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class Macros(BrowserView):
    def __getitem__(self, key):
        return self.template.macros[key]


class HeaderMacros(Macros):
    template = ViewPageTemplateFile('quills_header_macros.pt')


class WeblogEntryMacros(Macros):
    template = ViewPageTemplateFile('quills_entry_macros.pt')


class WeblogMacros(Macros):
    template = ViewPageTemplateFile('quills_weblog_macros.pt')



