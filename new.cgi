#!/usr/bin/perl -w
use strict;

use CGI;
use LWP::Simple;
use XML::Simple;
use POSIX qw( strftime );
use Date::Calc qw( Delta_Days );

use Data::Dumper;

# Cineworld's "syndication" XML doc - a massive record of all showings for all cinemas - several MB (*groan*)
my $src_url = 'http://www.cineworld.co.uk/syndication/listings.xml';

my $now = strftime( '%Y-%m-%dT00:00:00', gmtime() );
my ( $today ) = $now =~ m/(\d{4}-\d{2}-\d{2})/;

#$now = '2012-11-13T00:00:00';  # test

my $q = CGI->new();
print $q->header();
print $q->start_html( -title => 'Cineworld Edinburgh' );
print $q->h3( "Today and tomorrow at Cineworld Edinburgh" );
print $q->p( $now );

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
my $showing_tomorrow = {};

foreach my $film ( @films ) {  
  # Nasty fix for data inconsistency. Where there's only a single showing, XML::Simple is giving us a hashref and not an arrayref.
  if ( ref $film->{shows}->{show} eq 'HASH' ) {
    $film->{shows}->{show} = [ $film->{shows}->{show} ];
  }
  
  foreach my $show ( @{$film->{shows}->{show} } ) {
    if ( $show->{time} ge $now ) {
      my ( $show_date, $show_time ) = $show->{time} =~ m/(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}):\d{2}/;
      # We're not interested if the show is further away than tomorrow
      if ( Delta_Days( $today =~ /(\d{4})-(\d{2})-(\d{2})/, $show_date =~ /(\d{4})-(\d{2})-(\d{2})/ ) > 1 ) {
        next;
      }
      elsif ( $show_date eq $today ) {
        push( @{ $showing_today->{ make_title( $film, $show ) } }, "<a href=$root_url$show->{url}>$show_time</a>" );
      }
      else {
        push( @{ $showing_tomorrow->{ make_title( $film, $show ) } }, "<a href=$root_url$show->{url}>$show_time</a>" );
      }
    }
  }
}

# We've done all the hard work now - let's print it!

print "<pre>";
print "Today:<br>".Dumper( $showing_today );
print "Tomorrow:<br>".Dumper( $showing_tomorrow );
print "</pre>";

#print Dumper( $data );

sub make_title {
  my ( $film, $show ) = @_;
  
  my $title = $film->{title};
  $title =~ s/^(The|A) (.*$)/$2, $1/i;
  
  if ( defined $show->{videoType} ) {
    my $nice_type = $show->{videoType};
    $nice_type =~ s/imax/ (IMAX)/i;
    $nice_type =~ s/3d/ (3D)/i;
    $title .= $nice_type;
  }

  return $title;
}
