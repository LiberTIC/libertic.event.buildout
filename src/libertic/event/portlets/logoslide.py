#!/usr/bin/env python
# -*- coding: utf-8 -*-
__docformat__ = 'restructuredtext en'

from zope import schema
from zope.interface import implements
from zope.formlib import form
from zope.component import getMultiAdapter

from Products.CMFCore.utils import getToolByName
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from libertic.event import MessageFactory as _

class ILogoslidePortlet(IPortletDataProvider):
    """This portlet displays the data supplier or data operator logos
    """
    pass
    #~ portlet_title = schema.TextLine(
        #~ title=_(u'Portlet Title'),
        #~ description=_('help_portlet_title',
                      #~ default=u'Enter a title for this portlet. '
                               #~ "This property is used as the portlet's title in "
                               #~ 'the "@@manage-portlets" screen. '
                               #~ 'Leave blank for "Content portlet".'),
        #~ required=False,
    #~ )

class Assignment(base.Assignment):
    implements(ILogoslidePortlet)
    title = u'Libertic Logo slide Portlet'

class Renderer(base.Renderer):
    render = ViewPageTemplateFile('logoslide.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        context = self.context.aq_inner
        self.portal_state = getMultiAdapter((context, self.request),
                                       name=u'plone_portal_state')
        self.portal_url = self.portal_state.portal_url()
        self.hasName = False

class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()

# vim:set et sts=4 ts=4 tw=80:
