#!/usr/bin/env python
# -*- coding: utf-8 -*-
__docformat__ = 'restructuredtext en'

from zope import schema
from zope.interface import implements
from zope.formlib import form
from zope.component import getMultiAdapter
from Acquisition import aq_inner

from Products.CMFCore.utils import getToolByName
from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from libertic.event import MessageFactory as _

class ICarouselPortlet(IPortletDataProvider):
    """This portlet displays a caroussel with pictures
    """

class Assignment(base.Assignment):
    implements(ICarouselPortlet)
    title = u'Libertic carousel Portlet'
    

class Renderer(base.Renderer):
    render = ViewPageTemplateFile('carousel.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        context = self.context.aq_inner
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        portal_url = getToolByName(context, 'portal_url')
        self.navigation_root_path = portal_state.navigation_root_path()
        self.catalog = getToolByName(context, 'portal_catalog')

    def image_list(self):
        """Return a list of image according to a given folder
        """
        catalog = self.catalog
        folder_path = self.navigation_root_path + "/slideshow"
        images = catalog.searchResults({'portal_type': 'Image', 'path': {'query': folder_path, 'depth': 1}} )
        return images
        
class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()

    
# vim:set et sts=4 ts=4 tw=80:
