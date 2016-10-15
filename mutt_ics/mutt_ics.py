#!/usr/bin/env python
import io
import os
import re
import sys
from functools import partial, reduce
from operator import add
from dateutil import tz

import icalendar


datefmt = '%A, %d %B %Y, %H:%M %Z'


def compose(*functions):
    """
    Returns a function which acts as a composition of several `functions`. If
    one function is given it is returned if no function is given a
    :exc:`TypeError` is raised.

    >>> compose(lambda x: x + 1, lambda x: x * 2)(1)
    3

    .. note:: Each function (except the last one) has to take the result of the
              last function as argument.

    [ Shamelessly stolen from Brownie: https://github.com/DasIch/brownie ]
    """
    if not functions:
        raise TypeError('expected at least 1 argument, got 0')
    elif len(functions) == 1:
        return functions[0]
    return reduce(lambda f, g: lambda *a, **kws: f(g(*a, **kws)), functions)


def get_ics_text(f):
    """
    Loads the content from the stream and applies a workaround for Microsoft
    Exchange Server.
    """
    content = f.read()
    # Ugly workaround: Python datetime doesn't support dates earlier than 1900,
    # whilst Microsoft corp. has created it's Exchange Sever 2007 somewhere in
    # the beginning of XVII century. Yeah, right.
    hacks = {"STANDARD\nDTSTART:16010101": "STANDARD\nDTSTART:20071104",
             "DAYLIGHT\nDTSTART:16010101": "DAYLIGHT\nDTSTART:20070311"}
    for search, replace in hacks.items():
        ics_text = content.replace(search, replace)
    return ics_text


def get_interesting_stuff(cal):
    components = []
    for component in cal.subcomponents:
        c = get_component(component)
        if c is not None:
            components.append(c)
    return u'\n'.join(components)


def get_component(component):
    name = component.name
    if name == 'VCALENDAR':
        pass
    elif name == 'VTIMEZONE':
        pass
    elif name == 'VEVENT':
        return get_event(component)
    else:
        return None


def identity(x):
    return x


def format_date(x):
    return x.dt.astimezone(tz.tzlocal()).strftime(datefmt)


def get_event(e):
    unmailto = lambda x: re.compile('mailto:', re.IGNORECASE).sub('', x)
    def get_header(e):
        name_map = {'SUMMARY': 'Subject',
                    'ORGANIZER': 'Organizer',
                    'DTSTART': 'Start',
                    'DTEND': 'End',
                    'LOCATION': 'Location'}
        vals = []
        res = []

        def get_val(name, f):
            if name in e:
                vals.append((name_map[name], f(e[name])))

        get_val('SUMMARY', identity)
        get_val('ORGANIZER', unmailto)
        get_val('DTSTART', format_date)
        get_val('DTEND', format_date)
        get_val('LOCATION', identity)

        max_width = max(len(k) for k, v in vals)
        for k, v in vals:
            pad = u' ' * (max_width + 1 - len(k))
            line = u'%s:%s%s' % (k, pad, v)
            res.append(line)
        return u'\n'.join(res)

    def get_participants(e):
        participants = e.get('ATTENDEE', [])
        if not isinstance(participants, list):
            participants = [participants]
        if len(participants):
            people = map(compose(partial(add, u' ' * 4), unmailto),
                         participants)
            return u'Participants:\n%s' % "\n".join(people)
        else:
            return None

    def get_text_field(e, field, label):
        value = e.get(field, '').strip()
        if len(value):
            return u'%s:\n\n%s' % (label, value)
        else:
            return None

    result = filter(bool, [get_header(e),
                           get_participants(e),
                           get_text_field(e, 'DESCRIPTION', 'Description'),
                           get_text_field(e, 'COMMENT', 'Comment')])
    return u'\n'.join(result)


def main(args):
    if len(args) > 1 and os.path.isfile(args[1]):
        with io.open(args[1], 'r', encoding='utf-8') as f:
            ics_text = get_ics_text(f)
    else:
        stream = io.open(sys.stdin.fileno(), 'r', encoding='utf-8')
        ics_text = get_ics_text(stream)

    cal = icalendar.Calendar.from_ical(ics_text)
    output = get_interesting_stuff(cal)
    out_stream = io.open(sys.stdout.fileno(), 'w', encoding='utf-8')
    out_stream.write(output + '\n')


def entry_point():
    return main(sys.argv)


if __name__ == '__main__':
    entry_point()

# vi:set ts=4 sw=4 et sta:
