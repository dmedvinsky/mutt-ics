#!/usr/bin/env python
import os
import re
import sys
import codecs
from functools import partial, reduce
from operator import add

import icalendar


datefmt = '%A, %d %B %Y, %H:%M'


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
    ics_text = content.replace("\nDTSTART:1601", "\nDTSTART:1901")
    return ics_text


def get_interesting_stuff(cal):
    components = []
    for component in cal.subcomponents:
        c = get_component(component)
        if c is not None:
            components.append(c)
    return '\n'.join(components)


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


def get_event(e):
    unmailto = lambda x: re.compile('mailto:', re.IGNORECASE).sub('', x)
    def get_header(e):
        keys = [u'Subject', u'Organizer', u'Start', u'End', u'Location']
        vals = []
        if 'SUMMARY' in e:
            vals.append(('SUMMARY', e['SUMMARY']))
        if 'ORGANIZER' in e:
            vals.append(('ORGANIZER', unmailto(e['ORGANIZER'])))
        if 'DTSTART' in e:
            vals.append(('DTSTART', e['DTSTART'].dt.strftime(datefmt)))
        if 'DTEND' in e:
            vals.append(('DTEND', e['DTEND'].dt.strftime(datefmt)))
        if 'LOCATION' in e:
            vals.append(('LOCATION', e['LOCATION']))

        res = []
        max_width = max(map(len, keys))
        for k, v in vals:
            pad = u' ' * (max_width + 1 - len(k))
            line = u'%s:%s%s' % (k.capitalize(), pad, v)
            res.append(line)
        return '\n'.join(res)


    def get_participants(e):
        participants = e.get('ATTENDEE', [])
        if not isinstance(participants, list):
            participants = [ participants ]
        if len(participants):
            people = map(compose(partial(add, ' ' * 4), unmailto),
                         participants)
            return 'Participants:\n%s' % "\n".join(people)
        else:
            return None


    def get_description(e):
        description = e.get('DESCRIPTION', '').strip()
        if len(description):
            return 'Description:\n\n%s' % description
        else:
            return None

    result = filter(bool, [get_header(e),
                           get_participants(e),
                           get_description(e)])
    return "\n".join(result)


def main(args):
    if len(args) > 1 and os.path.isfile(args[1]):
        with codecs.open(args[1], 'rb', 'utf-8') as f:
            ics_text = get_ics_text(f)
    else:
        stream = codecs.getreader("utf-8")(sys.stdin)
        ics_text = get_ics_text(sys.stdin)

    cal = icalendar.Calendar.from_ical(ics_text)
    output = get_interesting_stuff(cal)
    sys.stdout.write(output)


if __name__ == '__main__':
    main(sys.argv)

# vi:set ts=4 sw=4 et sta:
