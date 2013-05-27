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

class Assignment(base.Assignment):
    implements(ILogoslidePortlet)
    title = u'Libertic Logo slide Portlet'

def userinfo_list(context, grpid):
    mtool = getToolByName(context, 'portal_membership')
    gtool = getToolByName(context, 'portal_groups')
    
    group = gtool.getGroupById(grpid) or None

    if not group:
        return []

    users = group.getGroupMembers()
    results = []

    for user in users:
        user_infos = {}
        personnal_infos = mtool.getMemberInfo(user.id)
        user_infos['fullname'] = personnal_infos['fullname']
        user_infos['logo'] = mtool.getPersonalPortrait(user.id) or None
        user_infos['home'] = mtool.getHomeUrl(user.id, verifyPermission=1);
        results.append(user_infos)    
    
    return results
    

class Renderer(base.Renderer):
    render = ViewPageTemplateFile('logoslide.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        context = self.context.aq_inner
        self.portal_state = getMultiAdapter((context, self.request),
                                       name=u'plone_portal_state')
        self.portal_url = self.portal_state.portal_url()
        
    @property
    def title(self):
        """return title of feed for portlet"""
        return getattr(self.data, 'portlet_title', '')
    
    def operators_list(self):
        """Return a list of operators, with name and portrait in each dict"""
        return userinfo_list(self.context, 'libertic_event_operator')

    def suppliers_list(self):
        """Return a list of operators, with name and portrait in each dict"""
        return userinfo_list(self.context, 'libertic_event_supplier')

class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()

    
# vim:set et sts=4 ts=4 tw=80:
