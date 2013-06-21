#!/usr/bin/env python
# -*- coding: utf-8 -*-
__docformat__ = 'restructuredtext en'


from zope.interface import Interface
from zope.component import getAdapter, getMultiAdapter, queryMultiAdapter, getUtility

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from plone.registry.interfaces import IRegistry
from plone.app.collection.interfaces import ICollection

from libertic.event.utils import users_from_group

from Acquisition import aq_parent

from five import grok
grok.templatedir('templates')

class EventListing(BrowserView):
    """Events listing view doc"""
    template = ViewPageTemplateFile('templates/libertic_event_datatables_view.pt')

    def __call__(self, **params):
        """."""
        params = {}
        return self.template(**params)

class MemberListing(BrowserView):
    """Operators or suppliers listing, from group operators"""

    #~ template = ViewPageTemplateFile('templates/member_list_view.pt')
    #~ 
    #~ def __call__(self, **params):
        #~ """."""
        #~ params = {}
        #~ return self.template(**params)

    def operators(self):
        """Operators infos"""
        context = self.context.aq_inner
        members = users_from_group(context, "libertic_event_operator")
        mtool = getToolByName(context, 'portal_membership')
        results = []
        for user in members:
            user_infos = {}
            memberdata = mtool.getMemberById(user.id)
            personnal_infos = mtool.getMemberInfo(user.id)
            user_infos['id'] = user.id
            user_infos['fullname'] = personnal_infos['fullname'] or user.id
            user_infos['location'] = personnal_infos['location'] or None
            user_infos['activity'] = personnal_infos['description'] or None
            user_infos['homeurl'] = personnal_infos['home_page'] or None

            results.append(user_infos)

        return results

    def suppliers(self):
        """Operators infos"""
        context = self.context.aq_inner
        members = users_from_group(context, "libertic_event_supplier")
        mtool = getToolByName(context, 'portal_membership')
        results = []
        for user in members:
            user_infos = {}
            memberdata = mtool.getMemberById(user.id)
            personnal_infos = mtool.getMemberInfo(user.id)
            user_infos['id'] = user.id
            user_infos['fullname'] = personnal_infos['fullname'] or user.id
            user_infos['location'] = personnal_infos['location'] or None
            user_infos['activity'] = personnal_infos['description'] or None
            user_infos['homeurl'] = personnal_infos['home_page'] or None

            results.append(user_infos)

        return results

# vim:set et sts=4 ts=4 tw=80:

