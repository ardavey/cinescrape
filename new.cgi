#!/usr/bin/perl -w
use strict;

use CGI;
use LWP::Simple;
use XML::Simple;
use POSIX qw( strftime );

use Data::Dumper;

# This is the page we're scraping
my $url = 'http://www.cineworld.co.uk/syndication/listings.xml';
my $today = strftime( "%a %d %b", gmtime() );
my $now   = strftime( "%H:%M", gmtime() );  # hardcode this for testing

my $q = CGI->new();
print $q->header();
print $q->start_html( -title => 'Cineworld Edinburgh' );
print $q->h3( "Today at Cineworld Edinburgh" );
print $q->p( "Showing after $now on $today" );

# grab the page and strip unnecessary whitespace
my $rawxml;
if ( open LOCALF, 'listings.xml' ) {
  print $q->p( 'using local file' );
  $rawxml = join( '', <LOCALF> );
  close LOCALF;
}
else {
  print $q->p( 'downloading file' );
  $rawxml = get $url;
}

my $xml = new XML::Simple( keyAttr => 'id' );
my $data = $xml->XMLin( $rawxml );
$data = $data->{cinema}->{21}->{listing};

print "<pre>".Dumper( $data )."</pre>";
