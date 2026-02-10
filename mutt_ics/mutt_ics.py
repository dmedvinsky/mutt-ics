#!/usr/bin/env python
import datetime
from dateutil import tz

import click
import icalendar


datefmt = '%A, %d %B %Y, %H:%M %Z'


# TODO: make configurable
colour_scheme = {'date': 'green',
                 'email': 'magenta',
                 'label': 'blue',
                 }


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


def write_element(component, name, label):
    if name not in component:
        return

    val = component[name]
    click.secho(f'{label:16}', fg=colour_scheme['label'], nl='')

    if isinstance(val, icalendar.vCalAddress):
        click.secho(val.email, fg=colour_scheme['email'])

    elif isinstance(val, icalendar.vDDDTypes):
        if isinstance(val.dt, datetime.date):
            local_time = val.dt
        else:
            local_time = val.dt.astimezone(tz.tzlocal())

        click.secho(local_time.strftime(datefmt), fg=colour_scheme['date'])

    elif isinstance(val, icalendar.vText):
        click.echo(val)

    else:
        click.secho(repr(val), fg='red')
        click.secho(dir(val), fg='yellow')


@click.command()
@click.argument("ics_file", type=click.File('r', encoding='utf-8'), default='-')
def main(ics_file):
    ics_text = get_ics_text(ics_file)

    cal = icalendar.Calendar.from_ical(ics_text)

    for component in cal.subcomponents:
        if component.name == 'VEVENT':
            write_element(component, 'SUMMARY', 'Summary')
            write_element(component, 'DESCRIPTION', 'Description')
            write_element(component, 'DURATION', 'Duration')
            write_element(component, 'DTSTART', 'Start')
            write_element(component, 'DTEND', 'End')
            write_element(component, 'STATUS', 'Status')

            write_element(component, 'LOCATION', 'Location')
            write_element(component, 'ORGANIZER', 'Organizer')
            write_element(component, 'ATTENDEE', 'Attendee')
            write_element(component, 'COMMENT', 'Comment')


if __name__ == '__main__':
    main()

# vi:set ts=4 sw=4 et sta:
