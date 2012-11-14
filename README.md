cinescrape
==========

This is intended to provide a lightweight page containing
upcoming Cinema showings for the current day.

Cineworld provide an XML syndication feed which is updated regularly.
A cron job runs to fetch this every hour, and the script parses it
to show only the showtimes for today and tomorrow in Edinburgh.

XML::Simple seems to be *painfully* slow for this volume of data -
will need to investigate other options at some point.