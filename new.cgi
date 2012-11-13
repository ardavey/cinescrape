#!/usr/bin/perl -w
use strict;

use CGI;
use LWP::Simple;
use XML::Simple;
use POSIX qw( strftime );

use Data::Dumper;

# Cineworld's "syndication" XML doc - a massive record of all showings for all cinemas - several MB (*groan*)
my $src_url = 'http://www.cineworld.co.uk/syndication/listings.xml';

my $now = strftime( '%Y-%m-%dT%H:%M:%S', gmtime() );
my ( $today ) = $now =~ m/(\d{4}-\d{2}-\d{2})/;

my $q = CGI->new();
print $q->header();
print $q->start_html( -title => 'Cineworld Edinburgh' );
print $q->h3( "Today at Cineworld Edinburgh" );
print $q->p( "Showing after $now on $today" );

my $rawxml;
if ( open LOCALF, 'listings.xml' ) {
  print $q->p( 'using local file' );
  $rawxml = join( '', <LOCALF> );
  close LOCALF;
}
else {
  print $q->p( 'downloading file' );
  $rawxml = get $src_url;
}

my $xml = new XML::Simple( keyAttr => 'id' );
my $data = $xml->XMLin( $rawxml );

# 21 == Edinburgh
$data = $data->{cinema}->{21};

my $root_url = $data->{root};
my @films = @{ $data->{listing}->{film} };

my $showing_today = {};
my $showing_later = {};

foreach my $film ( @films ) {  
  # Nasty fix for data inconsistency. Where there's only a single showing, they use a hashref and not an arrayref.
  if ( ref $film->{shows}->{show} eq 'HASH' ) {
    $film->{shows}->{show} = [ $film->{shows}->{show} ];
  }
  
  foreach my $show ( @{$film->{shows}->{show} } ) {
    if ( $show->{time} ge $now ) {
      my ( $show_date, $show_time ) = $show->{time} =~ m/(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}):\d{2}/;
      if ( $show_date eq $today ) {
        push( @{$showing_today->{$film->{title}}}, $show_time );
      }
      if ( $show_date gt $today ) {
        push( @{$showing_later->{$film->{title}}->{$show_date}}, $show_time );
      }
    }
  }
}

print "<pre>";
print "Today:<br>".Dumper( $showing_today );
print "Later:<br>".Dumper( $showing_later );
print "</pre>";

