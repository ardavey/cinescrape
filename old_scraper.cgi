#!/usr/bin/perl -w
use strict;

use CGI;
use LWP::Simple;
use POSIX qw( strftime );
use Data::Dumper;

# This is the page we're scraping
my $url = 'http://www.cineworld.co.uk/mobile/cinemas/21/nowshowing';

# Page content uses 'ddd DD mmm' format next to screening times
my $today = strftime( "%a %d %b", gmtime() );
my $now   = strftime( "%H:%M", gmtime() );  # hardcode this for testing

my $q = CGI->new();
print $q->header();
print $q->start_html( -title => 'Cineworld Edinburgh' );
print $q->h3( "Today at Cineworld Edinburgh" );
print $q->p( "Showing after $now on $today" );

# grab the page and strip unnecessary whitespace
my $content = get $url;

$content =~ s/\n//g;
$content =~ s/\s+/ /g;

# each movie is in a separate <div> - let's get our array on
my @films = $content =~ m!(<div class="film performances top".*?</div>)!g;
#my @films = $content =~ m!(<h2>(.*?)</h2>)!g;

#print "<hr>".join("<br>",@films)."<hr>";

# No need to go any further if there's nothing on!
if ( @films ) {
  my @showing_now = ();
  
  # carry out some ugly string matching to pick out the title and times.
  # skip any films which don't contain today's date in the block - they're not showing today!
  foreach my $film ( @films ) {
    next unless ( $film =~ m/$today/i );
    
    # parse out the times for this film
    my @times = $film =~ m/showing.*?>(\d\d:\d\d)/g;
    # and ditch those which are before now
    @times = grep { $_ gt $now } @times;
    # and get rid of duplicates
    @times = sort keys %{{ map { $_ => 1 } @times }};
    
    if ( @times ) {
      # there are showings remaining, so let's get the name and synopsis
      my ( $title ) = $film =~ m!\?film=\d+">(.*?)</a!;
      my ( $syn )   = $film =~ m!p class="clear">(.*?)</p!;  
      
      # if the title starts with '3D', 'The', 'A' or 'IMAX' then shift that to the end so we can sort it more usefully
      $title =~ s/^(IMAX)(?: -)? (.*$)/$2 ($1)/i;
      $title =~ s/(^[23])d - (.*$)/$2 ($1D)/i;
      $title =~ s/^(The|A) (.*$)/$2, $1/i;
      
      # Dump this row into the array
      my $row = "<td><b>$title</b><br>"
              . join( ', ', @times ) . "<br><br>"
              . "<small>$syn</small>";
      
      push( @showing_now, $row );
    }
  }
  
  if ( @showing_now ) {
    # we have films showing - let's sort them alphabetically and make a table
    @showing_now = sort @showing_now;
    
    print $q->start_table( {
                            -border      => 0,
                            -cellpadding => 2,
                            -cellspacing => 5,
                           } );
    
    my $count = 1;
    foreach my $row ( @showing_now ) {
      my $bgc = ( $count++ % 2 ) ? "lightgray" : "white";
      print $q->Tr( { -bgcolor => $bgc }, $row );
    }
    
    print $q->end_table();
  }
  else {
    print $q->h3( "Nothing showing today - check back tomorrow" );
  }
}
else {
  print $q->h3( "No movies found!" );
}

# Link to the cineworld site
print "<p><small><a href=\"$url\">Source page</a></small></p>";

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

print $q->small( "Andrew Davey 2011<br>" . ++$hits );

print $q->end_html();

# attempt to write the new hitcounter value to file
open HITWRITE, "> cine_hits";
print HITWRITE $hits;
close HITWRITE;

