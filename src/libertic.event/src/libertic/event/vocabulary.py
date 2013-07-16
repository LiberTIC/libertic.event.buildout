#!/usr/bin/env python
# -*- coding: utf-8 -*-
__docformat__ = 'restructuredtext en'

from zope import component
from zope import interface
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IVocabularyFactory

from five import grok

from plone.i18n.normalizer.base import baseNormalize
from plone.registry.interfaces import IRegistry

from libertic.event import MessageFactory as _
from libertic.event import interfaces
from libertic.event import utils

def uniquify(t):
    s = []
    [s.append(i) for i in t if not i in s]
    return s

class RegistryVocabularyFactory(object):
    """vocabulary to use with plone.app.registry"""
    interface.implements(IVocabularyFactory)
    def __init__(self, key):
        self.key = key

    def __call__(self, context, key=None):
        if not key: key=self.key
        registry = component.queryUtility(IRegistry)
        if registry is None: return []
        categories = registry[key]
        if not categories: categories = []
        categories = [utils.magicstring(c.strip()).decode('utf-8')
                      for c in categories]
        terms = [SimpleTerm(baseNormalize(category),
                            baseNormalize(category),
                            category)
                 for category in uniquify(categories)]
        return SimpleVocabulary(terms)


ProfileTypesVocabulary = RegistryVocabularyFactory('libertic.event.interfaces.ILiberticEventSiteSettings.profile_types')

#~ grok.global_utility(ProfileTypesVocabulary, name=u"ode.profile_types")

# vim:set et sts=4 ts=4 tw=80:
