## Script (Python) "removeCreatorFromAuthors"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##parameters=creator, authors
##title=Return true if we're in weblog content types
##

if context.meta_type == 'WeblogEntry' and creator in authors:
    authors.remove(creator)

return authors