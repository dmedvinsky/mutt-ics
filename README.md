Mutt ICS
========

Ever received a meeting notification in an email? Ever wanted to have a quick
glance at that `.ics` file and know what is that meeting about, where is it
going to happen and who is participating?

I did. So I made this little script.

Usage
-----

The package is on PyPI so it is pip-installable, but I recommend using PIP
Script Installer ([pipsi](https://github.com/mitsuhiko/pipsi)).

After installing with

    pipsi install mutt_ics

and making sure the `mutt-ics` executable is in your path, you should configure
mutt to use it to render ICS files. To do that, complete the following steps:

1. Add the following lines to your `.mailcap` file:

        text/calendar; mutt-ics; copiousoutput
        application/ics; mutt-ics; copiousoutput 

2. Add the following line to your `.muttrc` file:

        auto_view text/calendar application/ics

3. For `multipart/alternative` e-mails (which is what e.g. Outlook calendar generates),
   you probably want to prefer the `text/calendar` format view instead of its textual
   counterparts. For such settings add another line to the `.muttrc` config file:

        alternative_order text/calendar text/plain text/html


You're done. I guess. Maybe I forgot something. Please, file a ticket if I did.
