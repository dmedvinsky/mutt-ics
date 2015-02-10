# Mutt ICS

Ever received a meeting notification in an email? Ever wanted to have a quick
glance at that `.ics` file and know what is that meeting about, where is it
going to happen and who is participating?

I did. So I made this little script.

## Usage

For now this is kind of ugly, since I'm the only user of this. :-) Maybe one
day I'll make something decent out of this. Please file a ticket if you want to
give me a boost.

The steps are:

1. Clone the repository

        git clone git://github.com/dmedvinsky/mutt-ics mutt-ics

2. Install requirements (virtualenv recommended, though not necessary)

        cd mutt-ics
        virtualenv .env
        .env/bin/pip install -r requirements.txt
        PATH_TO_STUFF=`pwd`

3. Create a launcher script somewhere in your $PATH:

        cat > ~/bin/show_ics <<EOF
        #!/bin/sh
        export PYTHONIOENCODING=utf-8
        $PATH_TO_STUFF/.env/bin/python $PATH_TO_STUFF/src/main.py $@
        EOF
        chmod u+x ~/bin/show_ics

4. Add the following line in your `.mailcap` file:

        text/calendar;      ~/bin/show_ics; copiousoutput

5. Add the following line in your `.muttrc` file:

        auto_view text/calendar


You're done. I guess. Maybe I forgot something. Again, file a ticket if I did.

Thanks.
