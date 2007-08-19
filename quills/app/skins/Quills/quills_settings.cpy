## Controller Python Script "quills_settings"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Reconfigure Quills

REQUEST=context.REQUEST
portal_properties=context.portal_properties
portal_properties.editProperties(REQUEST)
portal_properties.quills_properties.manage_changeProperties(REQUEST)
context.portal_url.getPortalObject().manage_changeProperties(REQUEST)

from Products.CMFPlone import transaction_note
transaction_note('Reconfigured Quills')

return state.set(portal_status_message='Quills settings changed.')

# vim: set ft=python:
