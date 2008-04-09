from Products.Five.testbrowser import Browser as BaseBrowser

# Import PloneTestCase - this registers more products with Zope as a side effect
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import setupPloneSite


class Browser(BaseBrowser):

    def addAuthorizationHeader(self,
                               user=PloneTestCase.default_user,
                               password=PloneTestCase.default_password):
        """Add an authorization header using the given or default credentials.
        """
        self.addHeader('Authorization', 'Basic %s:%s' % (user, password))
        return self


class BrowserMixin:
    """A mixin class that makes it possible to get hold of a `browser' from
    tests.
    """

    def getBrowser(self, logged_in=False):
        """Instantiate and return a testbrowser for convenience.
        """
        browser = Browser()
        if logged_in:
            browser.addAuthorizationHeader()
        return browser
