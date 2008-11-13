# Plone imports
from Products.CMFCore.utils import getToolByName

def setup_gs_profiles(portal, profiles, out):
    setup_tool = getToolByName(portal, 'portal_setup')
    for extension_id in profiles:
        try:
            setup_tool.runAllImportStepsFromProfile('profile-%s' % extension_id)
        except Exception, e:
            print >> out, "Error while trying to GS import %s (%s, %s)" \
                          % (extension_id, repr(e), str(e))
            raise

