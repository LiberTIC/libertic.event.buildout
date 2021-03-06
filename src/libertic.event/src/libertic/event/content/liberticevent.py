#!/usr/bin/env python
# -*- coding: utf-8 -*-
__docformat__ = 'restructuredtext en'
import csv
from copy import deepcopy
from ordereddict import OrderedDict
import uuid as muuid
from five import grok
import datetime
import traceback
import DateTime
from zope import schema
from zope.schema.fieldproperty import FieldProperty
from StringIO import StringIO
from AccessControl.unauthorized import Unauthorized

from zope.interface import implements, alsoProvides
from z3c.form.interfaces import ActionExecutionError

from plone.directives import form
from z3c.form import button, field
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from plone.namedfile.field import NamedFile


from zope.interface import invariant, Invalid
from plone.dexterity.content import Container
from plone.app.dexterity.behaviors.metadata import IDublinCore
from plone.app.dexterity.behaviors.metadata import IPublication
from plone.directives import form, dexterity
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from plone.app.uuid.utils import uuidToObject
from icalendar import (
    Calendar as iCal,
    Event as iE,
    vCalAddress,
    vText,
)


from libertic.event.utils import (
    magicstring,
    ical_string,
)

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.uuid.interfaces import IUUID
from libertic.event import MessageFactory as _
try:
    import json
except:
    import simplejson as json

from libertic.event import interfaces as lei

class csv_dialect(csv.Dialect):
    delimiter = ','
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = '\n'
    quoting = csv.QUOTE_ALL


def export_csv(request, titles, rows, filename='file.csv'):
    output = StringIO()
    csvwriter = csv.DictWriter(
        output,
        fieldnames=titles,
        extrasaction='ignore',
        dialect = csv_dialect)
    titles_row = dict([(title, title) for title in titles])
    rows = [titles_row] + rows
    for i, row in enumerate(rows):
        for cell in row:
            if isinstance(row[cell], unicode):
                row[cell] = row[cell].encode('utf-8')
    csvwriter.writerows(rows)
    resp = output.getvalue()
    lresp = len(resp)
    request.response.setHeader('Content-Type','text/csv')
    request.response.addHeader(
        "Content-Disposition","filename=%s"%filename)
    request.response.setHeader('Content-Length', len(resp))
    request.response.write(resp)


def read_csv(fileobj):
    csvreader = csv.DictReader(fileobj, dialect = csv_dialect)
    rows = []
    for row in csvreader:
        rows.append(row)
    return rows


def empty_data():
    sdata =  {
        'address_details': None,
        'address': None,
        'audio_license': None,
        'audio_url': None,
        'author_email': None,
        'author_firstname': None,
        'author_lastname': None,
        'author_telephone': None,
        'contained': [],
        'cp': None,
        'country': None,
        'description': None,
        'effective': None,
        'eid': None,
        'email': None,
        'event_end': None,
        'event_start': None,
        'expires': None,
        'firstname': None,
        'language': None,
        'lastname': None,
        'latlong': None,
        'organiser': None,
        'capacity': None,
        'tarif_information:': None,
        'performers': tuple(),
        'photos1_license': None,
        'photos1_license': None,
        'photos1_url': None,
        'photos2_license': None,
        'photos2_url': None,
        'press_url': None,
        'related': [],
        'sid': None,
        'source': None,
        'subjects': tuple(),
        'target': None,
        'telephone': None,
        'title': None,
        'town': None,
        'video_license': None,
        'video_url': None,
    }
    return sdata

def data_from_ctx(ctx, **kw):
    pdb = kw.get('pdb', None)
    dc = IDublinCore(ctx)
    pub = IPublication(ctx)
    sdata =  {
        'address': ctx.address,
        'audio_license': ctx.audio_license,
        'audio_url': ctx.audio_url,
        'author_email': ctx.author_email,
        'author_firstname': ctx.author_firstname,
        'author_lastname': ctx.author_lastname,
        'author_telephone': ctx.author_telephone,
        'country': ctx.country,
        'cp': ctx.cp,
        'description': dc.description,
        'eid': ctx.eid,
        'email': ctx.email,
        'firstname': ctx.firstname,
        'language': dc.language,
        'lastname': ctx.lastname,
        'latlong': ctx.latlong,
        'location_name': ctx.location_name,
        'organiser': ctx.organiser,
        'capacity': ctx.capacity,
        'tarif_information': ctx.tarif_information,
        'performers': ctx.performers,
        'photos1_license': ctx.photos1_license,
        'photos1_url': ctx.photos1_url,
        'photos2_license': ctx.photos2_license,
        'photos2_url': ctx.photos2_url,
        'press_url': ctx.press_url,
        'sid': ctx.sid,
        'source': ctx.source,
        'subjects':  dc.subjects,
        'target': ctx.target,
        'telephone': ctx.telephone,
        'title': dc.title,
        'town': ctx.town,
        'video_license': ctx.video_license,
        'video_url': ctx.video_url,
    }
    # if we have not the values in dublincore, try to get them on context
    for k in 'language', 'title', 'description', 'subjects':
        if not sdata[k]:
            try:
                sdata[k] = getattr(ctx, k)
            except:
                continue
    def get_datetime_value(ctx, item):
        try:
            value = getattr(ctx, item)()
        except TypeError, ex:
            value = getattr(ctx, item)
        if isinstance(value, DateTime.DateTime):
            value.asdatetime()
        if isinstance(value, datetime.datetime):
            value = value.strftime(lei.datefmt)
        return value
    for item in ['effective', 'expires',
                 'event_start' ,'event_end',]:
        cctx = ctx
        if item in ['effective', 'expires']:
            cctx = pub
        sdata[item] = get_datetime_value(cctx, item)
    for relate in ['contained', 'related']:
        l = []
        for item in getattr(ctx, "%s_objs" % relate, []):
            #obj = item.to_object
            obj = item
            it = {"sid": obj.sid, "eid": obj.eid}
            if not it in l:
                l.append(it)
        sdata[relate] = l
    return sdata


alsoProvides(lei.ILiberticEvent, form.IFormFieldProvider)


class LiberticEvent(Container):
    implements(lei.ILiberticEvent)

    def database(self):
        return lei.IDatabaseGetter(self).database()

    @property
    def related_objs(self):
        val = []
        for uuid in self.related:
            obj = uuidToObject(uuid)
            if obj and not obj in val:
                val.append(obj)
        return val

    @property
    def contained_objs(self):
        val = []
        for uuid in self.contained:
            obj = uuidToObject(uuid)
            if obj and not obj in val:
                val.append(obj)
        return val


class AddForm(dexterity.AddForm):
    grok.name('libertic_event')
    grok.require('libertic.event.Add')

    def update(self):
        dexterity.AddForm.update(self)
        self.fields['eid'].field.required = False
        dexterity.AddForm.updateWidgets(self)

    def create(self, data):
        obj = dexterity.AddForm.create(self, data)
        obj.sid = data['sid']
        return obj

    def extractData(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        pm = getToolByName(self.context, 'portal_membership')
        user = pm.getAuthenticatedMember()
        userid = user.getId()
        data, errors = dexterity.AddForm.extractData(self)
        #sid = data.get('sid', None)
        sid = userid
        data['sid'] = sid
        eid = data.get('eid', None)
        if not eid:
            eid = muuid.uuid4().hex
            data['eid'] = eid
        unique_SID_EID_check(self.context, sid, eid)
        return data, errors

class EditForm(dexterity.EditForm):
    grok.context(lei.ILiberticEvent)
    grok.require('libertic.event.Edit')
    def update(self):
        dexterity.EditForm.update(self)
        self.fields['eid'].field.required = False
        dexterity.EditForm.updateWidgets(self)

    def applyChanges(self, data):
        if data.get("sid", None):
            self.context.sid = data["sid"]
        dexterity.EditForm.applyChanges(self, data)

    def extractData(self):
        data, errors = dexterity.EditForm.extractData(self)
        ctx_sid = getattr(self.context, 'sid', None)
        pm = getToolByName(self.context, 'portal_membership')
        user = pm.getAuthenticatedMember()
        userid = user.getId()
        sid = data.get('sid', ctx_sid)
        if not sid:
            sid = userid
        data['sid'] = sid
        eid = data.get('eid', None)
        if not eid:
            eid = muuid.uuid4().hex
            data['eid'] = eid
        editable_SID_EID_check(self.context, sid, eid)
        return data, errors

def unique_SID_EID_check(context, sid, eid, request=None, form=None, *args, **kw):
    db = lei.IDatabaseGetter(context).database()
    event = db.get_event(sid=sid, eid=eid)
    if event is not None:
        raise ActionExecutionError(
            Invalid(_(u"The SID/EID combination is already in use, "
                      "please adapt them.")))


def editable_SID_EID_check(context, sid, eid, request=None, form=None, *args, **kw):
    db = lei.IDatabaseGetter(context).database()
    events = [a for a in db.get_events(sid=sid, eid=eid)]
    uuids = [IUUID(a) for a in events]
    cuuid = IUUID(context)
    if (cuuid not in uuids) and bool(uuids):
        raise ActionExecutionError(
            Invalid(_(u"The SID/EID combination is already in use, "
                      "please adapt them.")))


class View(dexterity.DisplayForm):
    grok.context(lei.ILiberticEvent)
    grok.require('libertic.event.View')


class Json(grok.View):
    grok.context(lei.ILiberticEvent)
    grok.require('libertic.event.View')

    def render(self):
        sdata = data_from_ctx(self.context)
        resp = json.dumps(sdata)
        lresp = len(resp)
        self.request.response.setHeader('Content-Type','application/json')
        self.request.response.addHeader(
            "Content-Disposition","filename=%s.json" % (
                self.context.getId()))
        self.request.response.setHeader('Content-Length', len(resp))
        self.request.response.write(resp)


class Xml(grok.View):
    grok.context(lei.ILiberticEvent)
    grok.require('libertic.event.View')
    xml = ViewPageTemplateFile('liberticevent_templates/xml.pt')
    _macros = ViewPageTemplateFile('liberticevent_templates/xmacros.pt')
    @property
    def xmacros(self):
        return self._macros.macros

    def __call__(self):
        sdata = data_from_ctx(self.context)
        resp = self.xml(ctx=sdata).encode('utf-8')
        lresp = len(resp)
        self.request.response.setHeader('Content-Type','text/xml')
        self.request.response.addHeader(
            "Content-Disposition","filename=%s.xml" % (
                self.context.getId()))
        self.request.response.setHeader('Content-Length', len(resp))
        self.request.response.write(resp)


class Csv(grok.View):
    grok.context(lei.ILiberticEvent)
    grok.require('libertic.event.View')

    def render(self):
        sdata = data_from_ctx(self.context)
        for it in 'performers', 'subjects':
            sdata[it] = '|'.join(sdata[it])
        for it in 'related', 'contained':
            values = []
            for item in sdata[it]:
                values.append(
                    '%s%s%s' % (
                        item['sid'],
                        lei.SID_EID_SPLIT,
                        item['eid'],
                    ))
            sdata[it] = '|'.join(values)
        titles = sdata.keys()
        export_csv(
            self.request,
            titles,
            [sdata])


class Ical(grok.View):
    grok.context(lei.ILiberticEvent)
    grok.require('libertic.event.View')

    def ical_event(self):
        sdata = data_from_ctx(self.context)
        event = iE()
        sdata['ltitle'] = sdata['title']
        if sdata['source']:
            event['URL'] = sdata['source']
            sdata['ltitle'] += u' %(source)s' % sdata
        sub = sdata['subjects']
        desc = ['%(title)s', '%(source)s', '%(description)s']
        ssub = ''
        if sub:
            ssub = ', '.join([a.strip() for a in sub if a.strip()])
            desc.append(ssub)
        desc = [(a%sdata).strip() for a in desc if (a%sdata).strip()]
        if sdata['latlong']: event['GEO'] = sdata['latlong']
        if ssub: event['CATEGORIES'] = ssub
        event['UID'] = IUUID(self.context)
        event['SUMMARY'] = vText(sdata['ltitle'])
        event['DESCRIPTION'] = vText('; '.join(desc))
        event['LOCATION'] = vText(u'%(address)s %(address_details)s %(street)s, %(country)s' % sdata)
        event['DTSTART'] = sdata['event_start']
        event['DTEND'] = sdata['event_end']
        return event

    def render(self):
        sdata = magicstring(ical_string(self.ical_event()))
        resp = magicstring(sdata)
        lresp = len(resp)
        self.request.response.setHeader('Content-Type','text/calendar')
        self.request.response.addHeader(
            "Content-Disposition","filename=%s.ics" % (
                self.context.getId()))
        self.request.response.setHeader('Content-Length', len(resp))
        self.request.response.write(resp)



def supplier_authorized(roles):
    auth = ['Manager',
            'LiberticSupplier',
            'Site Administrator'
           ]
    for r in auth:
        if r in roles:
            return True
    return False


class EventApiUtil(grok.Adapter):
    grok.context(lei.IDatabase)
    grok.implements(lei.IEventApiUtil)

    def __init__(self, context):
        self.context = context

    def mapply(self, grabber, contents, **kwargs):
        db = self.context
        pdb = kwargs.get('pdb', None)
        catalog = getToolByName(self.context, 'portal_catalog')
        pm = getToolByName(self.context, 'portal_membership')
        user = pm.getAuthenticatedMember()
        userid = user.getId()
        sid = userid
        # must be supplier on context
        results = {'results': [], 'messages': [], 'status': 1}
        result = {
            'eid': None,
            'sid': sid,
            'url': None,
            'title': None,
            'status': None,
            'messages': [],
        }
        try:
            if not supplier_authorized(
                user.getRolesInContext(db)):
                raise Unauthorized()
            grabber = getUtility(lei.IEventsGrabber, name=grabber)
            datas = grabber.data(contents)
            secondpass_datas = []
            for data in datas:
                res = deepcopy(result)
                try:
                    res['eid'] = data['transformed']['eid']
                except Exception, ex:
                    try:
                        res['eid'] = data['initial'].get('eid', None)
                    except Exception, ex:
                        pass

                #try:
                #    res['sid'] = data['transformed']['sid']
                #except Exception, ex:
                #    try:
                #        res['sid'] = data['initial'].get('sid', None)
                #    except Exception, ex:
                #        pass
                try:
                    cdata = deepcopy(data)
                    for k in ['contained', 'related']:
                        if k in cdata:
                            del cdata[k]
                    infos, ret, event = lei.IDBPusher(db).push_event(cdata, [userid], sid=sid)
                    if event is not None:
                        event.reindexObject()
                        res['url'] = event.absolute_url()
                        res['title'] =  "%s - %s - %s" % (
                            event.title, event.sid, event.eid)
                    if infos:
                        if isinstance(infos, list):
                            res['messages'].extend(infos)
                        else:
                            res['messages'].append(infos)
                except Exception, e:
                    trace = traceback.format_exc()
                    ret = 'failed'
                    res['messages'].append(trace)
                res['status'] = ret
                if ret in ['created', 'edited']:
                    secondpass_datas.append(data)
                results['results'].append(res)
            # when we finally have added / edited, set the references
            for data in secondpass_datas:
                try:
                    cdata = deepcopy(data)
                    infos, ret, event = lei.IDBPusher(db).push_event(cdata, [user.getId()], sid=sid)
                    if event is not None:
                        event.reindexObject()
                except Exception, e:
                    trace = traceback.format_exc()
                    res = deepcopy(result)
                    res['status'] = 2
                    res['eid'] = data['eid']
                    res['sid'] = data['sid']
                    res['messages'].append(trace)
                    results['results'].append(res)
        except Exception, e:
            results['status'] = 0
            trace = traceback.format_exc()
            results['messages'].append(trace)
        return results

class _api(grok.View):
    grok.baseclass()
    grok.context(lei.IDatabase)
    grok.require('libertic.eventsdatabase.View')
    mimetype = None
    type = None

    def get_contents(self):
        try:
            contents = self.request.stdin.getvalue()
        except:
            contents = self.request.read()
            self.request.seek(0)
        return contents

    def create(self, *args, **kw):
        pdb = kw.get('pdb', None)
        results = lei.IEventApiUtil(self.context).mapply(
            self.grabber,
            self.get_contents(),
            pdb=pdb)
        resp = self.serialize_create(results)
        lresp = len(resp)
        self.request.response.setHeader('Content-Type', self.mimetype)
        self.request.response.addHeader(
            "Content-Disposition","filename=%s.%s" % (
                self.context.getId(), self.type))
        self.request.response.setHeader('Content-Length', len(resp))
        self.request.response.write(resp)

    def serialize_create(self, datas):
        return datas

    def render(self, **kw):
        pdb = kw.get('pdb', None)
        mtd = self.request.method.upper()
        mtds = {'GET': 'get',
                'POST': 'create',
               }
        if mtd in mtds:
            return getattr(self, mtds[mtd])(pdb=pdb)

class json_api(_api):
    grabber = 'jsonapi'
    mimetype = 'application/json'
    type = 'json'

    def serialize_create(self, datas):
        return json.dumps(datas)

class xml_api(_api):
    grabber = 'xmlapi'
    mimetype = 'text/xml'
    type = 'xml'
    api_template = ViewPageTemplateFile('liberticevent_templates/api.pt')

    def serialize_create(self, datas):
        sdata = {'data': datas}
        resp = self.api_template(**sdata).encode('utf-8')
        return resp


class IFileImportFields(form.Schema):
    ev_file = NamedFile(title=_(u"Events file"))
    ev_format = schema.Choice(
        title=_(u"Events file format"),
        description=_(u"Can be empty if the extension is one of : csv, json, xml"),
        required=False,
        vocabulary="lev_formats_imp")


class file_import(form.Form):
    """"""
    # This form is available at the site root only
    grok.context(lei.IDatabase)
    ignoreContext = True
    fields = field.Fields(IFileImportFields)
    grok.require("libertic.event.Add")

    @button.buttonAndHandler(u'Ok')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        ev_format = data['ev_format']
        ev_fn = data['ev_file'].filename
        ev_data = data['ev_file'].data
        if not ev_format and ev_fn:
            if '.' in ev_fn:
                ext = ev_fn.split('.')[-1]
                if ext in ['xml', 'json', 'csv']:
                    ev_format = '%sapi' % ext

        self.description = []
        stats_msg, desc = '', ''
        __ = self.context.translate
        if not ev_format:
            self.status = __(_('Invalid File/Format'))
        else:
            results = lei.IEventApiUtil(self.context).mapply(
                ev_format, ev_data)
            statuses, nb = {}, 0
            if results['status'] == 0:
                self.status = __(
                    _('There were fatal errors during import'))
            else:
                self.status = __(
                    _('Events import has run sucessfully, '
                      'please check the following log'))
            links = OrderedDict()
            links['created'] = ['<ul>']
            links['edited'] = ['<ul>']
            links['failed'] = []
            if results['status'] > 0:
                for item in results['results']:
                    nb += 1
                    res = item.get('status', None)
                    if res:
                        if not res in statuses:
                            statuses[res] = 0
                        statuses[res] += 1
                    if res in ['created', 'edited']:
                        if item['url']:
                            links[res].append(
                                '<li>'
                                '<a href="%(url)s">'
                                '%(title)s'
                                '</a>'
                                '</li>' % item
                            )
                    if res == 'failed':
                        msg = '<ul class="failed-item">'

                        msg += '\n'.join(['<li><pre>%s</pre></li>' % m
                                          for m in item['messages']])
                        msg += '</ul>'
                        links[res].append(msg)
                links['created'].append('</ul>')
                links['edited'].append('</ul>')
                if nb:
                    stats_msg += (
                        '<div class="lei-import-stats">'
                        '<p>%s</p>'
                        '<ul>') % (
                            __(
                                _('${nb} Elements processed in the file',
                                  mapping={'nb': nb})))
                    for i in statuses:
                        stats_msg += '<li>%s : %s</li>' % (
                            __(_(i)), statuses[i]
                        )
                    stats_msg += '</ul></div>'
                    desc += '<div class="detailed-import">'
                    for i in links:
                        llen = statuses.get(i, 0)
                        if llen:
                            desc += '<dl class="detailed-%s collapsible collapsedOnLoad">' % i
                            desc += '<dt class="collapsibleHeader">%s %s %s</dt>' % (
                                llen, __(_(i)), __(_('Events')))
                            desc += '<dd class="collapsibleContent">'
                            desc += '\n'.join(links[i])
                            desc += '</dd>'
                            desc += '</dl>'
                    desc += '</div>'
        self.description.append(stats_msg)
        self.description.append(desc)
        self.description = '\n'.join(self.description)


# vim:set et sts=4 ts=4 tw=80:
