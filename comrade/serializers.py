from django.core.serializers.json import Serializer as JSONSerializer
from django.db.models.query import QuerySet
from django.db.models import Model
from django.utils.encoding import smart_str, smart_unicode
from django.http import HttpResponse

from StringIO import StringIO
import decimal, inspect

class UniversalJSONSerializer(JSONSerializer):

    def serialize(self, data, **options):
        """
        Serialize ANYTHING.
        """
        self.options = options

        self.stream = options.get("stream", StringIO())
        self.selected_fields = options.get("fields")
        self.use_natural_keys = options.get("use_natural_keys", False)
        self.typemapper = options.get("typemapper", {})

        self.start_serialization()
        self.objects = self._construct(data)
        self.end_serialization()
        return self.getvalue()

    def _construct(self, data):
            """
            Recursively serialize a lot of types, and
            in cases where it doesn't recognize the type,
            it will fall back to Django's `smart_unicode`.

            Borrowed from django-piston.

            Returns `dict`.
            """
            def _any(thing, fields=None):
                """
                Dispatch, all types are routed through here.
                """
                ret = None

                if isinstance(thing, QuerySet):
                    ret = _qs(thing, fields)
                elif isinstance(thing, (tuple, list, set)):
                    ret = _list(thing, fields)
                elif isinstance(thing, dict):
                    ret = _dict(thing, fields)
                elif isinstance(thing, decimal.Decimal):
                    ret = str(thing)
                elif isinstance(thing, Model):
                    ret = _model(thing, fields)
                elif isinstance(thing, HttpResponse):
                    raise HttpStatusCode(thing)
                elif inspect.isfunction(thing):
                    if not inspect.getargspec(thing)[0]:
                        ret = _any(thing())
                elif hasattr(thing, '__emittable__'):
                    f = thing.__emittable__
                    if inspect.ismethod(f) and len(inspect.getargspec(f)[0]) == 1:
                        ret = _any(f())
                elif repr(thing).startswith("<django.db.models.fields.related.RelatedManager"):
                    ret = _any(thing.all())
                else:
                    ret = smart_unicode(thing, strings_only=True)

                return ret

            def _fk(data, field):
                """
                Foreign keys.
                """
                return _any(getattr(data, field.name))

            def _related(data, fields=None):
                """
                Foreign keys.
                """
                return [ _model(m, fields) for m in data.iterator() ]

            def _m2m(data, field, fields=None):
                """
                Many to many (re-route to `_model`.)
                """
                return [ _model(m, fields) for m in getattr(data, field.name).iterator() ]

            def _model(data, fields=None):
                """
                Models. Will respect the `fields` and/or
                `exclude` on the handler (see `typemapper`.)
                """
                ret = { }
                handler = self.in_typemapper(type(data))
                get_absolute_uri = False

                if handler or fields:
                    v = lambda f: getattr(data, f.attname)

                    if handler:
                        fields = getattr(handler, 'fields')    
                    
                    if not fields or hasattr(handler, 'fields'):
                        """
                        Fields was not specified, try to find teh correct
                        version in the typemapper we were sent.
                        """
                        mapped = self.in_typemapper(type(data))
                        get_fields = set(mapped.fields)
                        exclude_fields = set(mapped.exclude).difference(get_fields)

                        if 'absolute_uri' in get_fields:
                            get_absolute_uri = True

                        if not get_fields:
                            get_fields = set([ f.attname.replace("_id", "", 1)
                                for f in data._meta.fields + data._meta.virtual_fields])
                        
                        if hasattr(mapped, 'extra_fields'):
                            get_fields.update(mapped.extra_fields)

                        # sets can be negated.
                        for exclude in exclude_fields:
                            if isinstance(exclude, basestring):
                                get_fields.discard(exclude)

                            elif isinstance(exclude, re._pattern_type):
                                for field in get_fields.copy():
                                    if exclude.match(field):
                                        get_fields.discard(field)

                    else:
                        get_fields = set(fields)

                    met_fields = self.method_fields(handler, get_fields)

                    for f in data._meta.local_fields + data._meta.virtual_fields:
                        if f.serialize and not any([ p in met_fields for p in [ f.attname, f.name ]]):
                            if not f.rel:
                                if f.attname in get_fields:
                                    ret[f.attname] = _any(v(f))
                                    get_fields.remove(f.attname)
                            else:
                                if f.attname[:-3] in get_fields:
                                    ret[f.name] = _fk(data, f)
                                    get_fields.remove(f.name)

                    for mf in data._meta.many_to_many:
                        if mf.serialize and mf.attname not in met_fields:
                            if mf.attname in get_fields:
                                ret[mf.name] = _m2m(data, mf)
                                get_fields.remove(mf.name)

                    # try to get the remainder of fields
                    for maybe_field in get_fields:
                        if isinstance(maybe_field, (list, tuple)):
                            model, fields = maybe_field
                            inst = getattr(data, model, None)

                            if inst:
                                if hasattr(inst, 'all'):
                                    ret[model] = _related(inst, fields)
                                elif callable(inst):
                                    if len(inspect.getargspec(inst)[0]) == 1:
                                        ret[model] = _any(inst(), fields)
                                else:
                                    ret[model] = _model(inst, fields)

                        elif maybe_field in met_fields:
                            # Overriding normal field which has a "resource method"
                            # so you can alter the contents of certain fields without
                            # using different names.
                            ret[maybe_field] = _any(met_fields[maybe_field](data))

                        else:
                            maybe = getattr(data, maybe_field, None)
                            if maybe is not None:
                                if callable(maybe):
                                    if len(inspect.getargspec(maybe)[0]) <= 1:
                                        ret[maybe_field] = _any(maybe())
                                else:
                                    ret[maybe_field] = _any(maybe)
                            else:
                                handler_f = getattr(handler or self.handler, maybe_field, None)

                                if handler_f:
                                    ret[maybe_field] = _any(handler_f(data))

                else:
                    for f in data._meta.fields:
                        ret[f.attname] = _any(getattr(data, f.attname))

                    fields = dir(data.__class__) + ret.keys()
                    add_ons = [k for k in dir(data) if k not in fields]

                    for k in add_ons:
                        ret[k] = _any(getattr(data, k))

                # resouce uri
                if self.in_typemapper(type(data)):
                    handler = self.in_typemapper(type(data))
                    if hasattr(handler, 'resource_uri'):
                        url_id, fields = handler.resource_uri(data)

                        try:
                            ret['resource_uri'] = reverser( lambda: (url_id, fields) )()
                        except NoReverseMatch, e:
                            pass

                if hasattr(data, 'get_api_url') and 'resource_uri' not in ret:
                    try: ret['resource_uri'] = data.get_api_url()
                    except: pass

                # absolute uri
                if hasattr(data, 'get_absolute_url') and get_absolute_uri:
                    try: ret['absolute_uri'] = data.get_absolute_url()
                    except: pass

                return ret

            def _qs(data, fields=None):
                """
                Querysets.
                """
                return [ _any(v, fields) for v in data ]

            def _list(data, fields=None):
                """
                Lists.
                """
                return [ _any(v, fields) for v in data ]

            def _dict(data, fields=None):
                """
                Dictionaries.
                """
                return dict([ (k, _any(v, fields)) for k, v in data.iteritems() ])

            # Kickstart the seralizin'.
            return _any(data, self.selected_fields)

    def in_typemapper(self, model):
        for klass, (km, is_anon) in self.typemapper.iteritems():
            if model is km and is_anon:
                return klass
