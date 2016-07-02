#!/usr/bin/perl -w
use strict;

use CGI;
use LWP::Simple;
use XML::Simple;
use POSIX qw( strftime );
use Date::Calc qw( Delta_Days );

use Data::Dumper;

# Cineworld's "syndication" XML doc - a massive record of all showings for all cinemas - several MB (*groan*)
# TODO: Some kind of caching of this data.  CW seem to update it regularly (hourly?) so perhaps
# a cron job to fetch it and we can just use the local copy.
my $src_url = 'http://www.cineworld.co.uk/syndication/listings.xml';

my $now = strftime( '%Y-%m-%dT00:00:00', gmtime() );
my ( $today ) = $now =~ m/(\d{4}-\d{2}-\d{2})/;

my $q = CGI->new();
print $q->header();

# Super-simple title info and today's date
print $q->start_html( -title => 'Cineworld Edinburgh - Today/Tomorrow' );
print '<span style="width: 95%; font-family: sans-serif;">';
print $q->h2( "$today" );

# We read the data from a local file if it exists
my $raw_xml = get_raw_xml();

my $xml = new XML::Simple( keyAttr => 'id' );
my $data = $xml->XMLin( $raw_xml, ForceArray => [ 'show' ] );
$data = $data->{cinema}->{21};  # We're only interested in Edinburgh for now

my $root_url = $data->{root};
my @films = @{ $data->{listing}->{film} };

my $showing_today = {};
my $showing_tomorrow = {};

foreach my $film ( @films ) {    
  foreach my $show ( @{$film->{shows}->{show} } ) {
    if ( $show->{time} ge $now ) {
      my ( $show_date, $show_time ) = $show->{time} =~ m/(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}):\d{2}/;
      # We're not interested if the show is further away than tomorrow
      if ( Delta_Days( $today =~ /(\d{4})-(\d{2})-(\d{2})/, $show_date =~ /(\d{4})-(\d{2})-(\d{2})/ ) > 1 ) {
        next;
      }
      elsif ( $show_date eq $today && $show->{time} ge $now ) {
        #push( @{ $showing_today->{ make_title( $film, $show ) } }, "<a href=$root_url$show->{url}>$show_time</a>" );
        push( @{ $showing_today->{ make_title( $film, $show ) } }, $show_time );
      }
      else {
        #push( @{ $showing_tomorrow->{ make_title( $film, $show ) } }, "<a href=$root_url$show->{url}>$show_time</a>" );
        push( @{ $showing_tomorrow->{ make_title( $film, $show ) } }, $show_time );
      }
    }
  }
}

# We've done all the hard work now - let's print it!
print_table( 'Today:', $showing_today );
print_table( 'Tomorrow:', $showing_tomorrow );
hit_counter();

#-------------------------------------------------------------------------------

sub get_raw_xml {
  my $raw_xml = '';
  if ( open LOCALF, 'listings.xml' ) {
    print "\n\n<!-- using local data -->\n\n";
    $raw_xml = join( '', <LOCALF> );
    close LOCALF;
  }
  else {
    print "\n\n<!-- downloading data -->\n\n";
    $raw_xml = get $src_url;
  }
  return $raw_xml;
}

sub make_title {
  my ( $film, $show ) = @_;
  
  my $title = $film->{title};
  $title =~ s/^\(.*?\) //;
  $title =~ s/^(The|A) (.*$)/$2, $1/i;
  
  if ( defined $show->{videoType} ) {
    my $nice_type = uc( $show->{videoType} );
    $nice_type =~ s/^(.*)$/ ($1)/;
    $title .= $nice_type;
  }

  return $title;
}

sub print_table {
  my ( $label, $showings ) = @_;

  print $q->hr();
  print $q->h3( $label );

  if ( scalar keys %$showings == 0 ) {
    print $q->p( 'Nothing to see' );
  }
  else {
    print $q->start_table( {
                          -border      => 0,
                          -cellpadding => 5,
                          -cellspacing => 5,
                          -width       => "100%",
                        } );
    
    my $count = 1;
    foreach my $title ( sort keys %$showings ) {
      my $bgc = ( $count++ % 2 ) ? "lightgray" : "white";
      print $q->Tr( { -bgcolor => $bgc },
                   $q->td( "<b>$title</b><br>".join( ' ', sort( @{ $showings->{$title} } ) ) ),
                  );
    }
    
    print $q->end_table();
  }
}

sub hit_counter {
  print $q->hr();
  
  # very simple hit counter - I want to see if anyone else is using this!
  my $hits;
  
  # 'hits' is a txt file where the first row represents the number of hits
  if ( -e "./cine_hits" ) {
    open HITREAD, "< cine_hits";
    my @in = <HITREAD>;
    close HITREAD;
    chomp @in;
    $hits = $in[0];
  }
  else {
    $hits = 0;
  }
  
  print $q->small( "gr00ved 2012<br>" . ++$hits );
  
  print '</span>';
  print $q->end_html();
  
  # attempt to write the new hitcounter value to file
  open HITWRITE, "> cine_hits";
  print HITWRITE $hits;
  close HITWRITE;
}
