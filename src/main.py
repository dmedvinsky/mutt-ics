#!/usr/bin/env python
import os
import sys
from functools import partial
from operator import add

import icalendar
from brownie.functional import compose


datefmt = '%A, %d %B %Y, %H:%M'


def get_ics_text(f):
    """
    Loads the content from the stream and applies a workaround for Microsoft
    Exchange Server.
    """
    content = f.read()
    # Ugly workaround: Python datetime doesn't support dates earlier than 1900,
    # whilst Microsoft corp. has created it's Exchange Sever 2007 somewhere in
    # the beginning of XVII century. Yeah, right.
    ics_text = content.replace("\nDTSTART:1601","\nDTSTART:1901")
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
    unmailto = lambda x: x.replace('MAILTO:', '')
    def get_header(e):
        keys = ['Subject', 'Organizer', 'Start', 'End', 'Location']
        vals = [unicode(e['SUMMARY']),
                unmailto(unicode(e['ORGANIZER'])),
                e['DTSTART'].dt.strftime(datefmt),
                e['DTEND'].dt.strftime(datefmt),
                unicode(e['LOCATION'])]
        res = []
        w = max(map(len, keys))
        for k, v in zip(keys, vals):
            pad = ' ' * (w + 1 - len(k))
            res.append(u'%s:%s%s' % (k.capitalize(), pad, v))
        return u'\n'.join(res)

    def get_participants(e):
        if 'ATTENDEE' not in e:
            return None

        participants = e['ATTENDEE']
        if not isinstance(participants, list):
            participants = [ participants ]
        if len(participants):
            people = map(compose(partial(add, ' ' * 4), unmailto, unicode),
                         participants)
            return u'\nParticipants:\n%s' % u'\n'.join(people)
        else:
            return None

    def get_description(e):
        description = unicode(e['DESCRIPTION']).strip()
        if len(description):
            return u'\nDescription:\n\n%s' % description
        else:
            return None

    result = filter(bool, [get_header(e),
                           get_participants(e),
                           get_description(e)])
    return u'\n'.join(result)


def main(args):
    if len(args) > 1 and os.path.isfile(args[1]):
        with open(args[1]) as f:
            ics_text = get_ics_text(f)
    else:
        ics_text = get_ics_text(sys.stdin)

    cal = icalendar.Calendar.from_ical(ics_text)
    output = get_interesting_stuff(cal)
    print output.encode('utf-8')



if __name__ == '__main__':
    main(sys.argv)
