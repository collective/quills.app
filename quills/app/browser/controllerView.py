from quills.app.browser.baseview import BaseView
from Products.CMFCore.utils import getToolByName

# A basic form controller designed for maximum compatibility with CMFFormController
# i.e. changes to the existing templates are minimised.
# n.b. this should probably be phased out again at some time by using formlib
# but for the time being it's rather useful to have.
# Written by Andreas Zeidler a.k.a. witsch based on the `FormControllerView` in membrane
# (http://dev.plone.org/collective/browser/membrane/trunk/browser/tool_zmi_views.py?rev=21197)

class FormControllerViewState:
    """ fake formcontroller's state class for page templates """
    
    def __init__(self, errors):
        self.errors = errors
    
    def getErrors(self, *args, **kw):

        return self.errors
    

class FormControllerView(BaseView):
    """ a very basic formcontroller-like view class """
    
    def __call__(self, *args, **kw):
        self.args = args
        self.kw = kw
        errors = {}
        if self.request.get('submitted', None) or self.request.get('form.submitted', None):
            errors = self.validate()
            if not errors:
                errors = self.control()
                if not errors:
                    return self.action(*args, **kw)
            elif type(errors) == type(''):      # a redirection was given...
                return self.callByName(errors)
        return self.callIndex(errors, *args, **kw)
    
    def validate(self):
        """ performs validation and returns an errors dictionary """
        return {}
    
    def control(self):
        """ performs the actions after a successful validation possibly
            returning an errors dictionary """
        return {}
    
    def action(self, *args, **kw):
        """ this can be called to return some output or redirect to another
            page after the control action was successfully called """
        return self.callIndex(*args, **kw)
    
    def translate(self, msg):
        ltool = getToolByName(self.context, 'portal_languages')
        lang = ltool.getPreferredLanguage()
        panel = getToolByName(self.context, 'Control_Panel')
        return panel.TranslationService.utranslate(msgid=msg,
            domain='quills', target_language=lang, context=self.context)
    
    def translateErrors(self, errors):
        translated = {}
        for field, msg in errors.items():
            if type(msg) == type(()):
                if len(msg) == 2:
                    msgstr, msgid = msg
                else:
                    msgstr, msgid = msg[0], msg[0]
                msg = self.translate(msgid)
                if msg == msgid:
                    msg = self.translate(msgstr)
            translated[field] = msg
        return translated
    
    def callIndex(self, errors={}, *args, **kw):
        """ call the original template with some additional parameters """
        errors = self.translateErrors(errors)
        return self.index(errors=errors, 
            state=FormControllerViewState(errors), *args, **kw)
            
    def callByName(self, name, errors={}):
        """ call the original template with some additional parameters """
        obj = getattr(self.context, name)
        errors = self.translateErrors(errors)
        return obj(errors=errors, 
            state=FormControllerViewState(errors), *self.args, **self.kw) 

    def setMessage(self, msg):
        self.request.set('portal_status_message', msg)
    
    def getToolByName(self, name):
        """ helper function to return the named portal tool """
        return getToolByName(self.context, name, None)
    
    def getFormVar(self, name):
        """ return the value of a request variable or None """
        var = self.request.get(name, None)
        if var is not None and type(var) == type(''):
            var = var.strip()
        return var
