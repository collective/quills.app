import unittest
from doctest import DocTestSuite

# Zope imports
import zope.component.testing

def setUp(test):
    pass

suites = (
    DocTestSuite('quills.app.topic',
                 setUp=zope.component.testing.setUp,
                 tearDown=zope.component.testing.tearDown),
    DocTestSuite('quills.app.archive',
                 setUp=zope.component.testing.setUp,
                 tearDown=zope.component.testing.tearDown),
    DocTestSuite('quills.app.weblogentrybrain',
                 setUp=zope.component.testing.setUp,
                 tearDown=zope.component.testing.tearDown),
    DocTestSuite('quills.app.browser.weblogview',
                 setUp=zope.component.testing.setUp,
                 tearDown=zope.component.testing.tearDown),
    )

def test_suite():
    return unittest.TestSuite(suites)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')