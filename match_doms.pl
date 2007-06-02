#!/usr/bin/perl

# parse_nicknames.pl
# John Jacobsen, NPX Designs, Inc., jacobsen\@npxdesigns.com
# Started: Sun Jan 28 11:32:10 2007 TEST
# Insert DOMs with known positions from nicknames.txt into default-dom-geometry.xml

package MY_PACKAGE;
use strict;

my $nicknames = "./nicknames.txt";
my $geomfile  = "./default-dom-geometry.xml";

die "Can't find $nicknames" unless -f $nicknames;
die "Can't find $geomfile" unless -f $geomfile;

open(NICK, $nicknames) or die "Can't open $nicknames: $!\n";

my @mbids;
my %domidof;
my %nameof;
my %stringof;
my %posof;
my %inGeom;

# Get nickname data
while(my $line = <NICK>) {
    #print $line;
    if($line =~ /^(\S+)\s+(\S+)\s+(\S+)\s+(\d+)\-(\d+)/) {
	#print "$1 $2 $3 $4 $5\n";
	push @mbids, $1;
	$domidof{$1}  = $2;
	$nameof{$1}   = $3;
	$stringof{$1} = $4;
	$posof{$1}    = int($5);
	$inGeom{$1}   = 0;
    }
}
close NICK;

my $geom = `cat $geomfile`;
my (@ddDoms, %ddStringOf, %ddPosOf, %ddNameOf, %ddProdOf, %ddxof, %ddyof, %ddzof, %ddIsNew);
my (%strPosToX, %strPosToY, %strPosToZ);

# Parse deployed-doms geometry file
while($geom =~ m|<string>(.+?)</string>|sg) {
    my $stringContents = $1;
    next unless $stringContents =~ m|<number>(\d+)</number>|;
    my $stringNum = $1;
    while($stringContents =~ m|<dom>(.+?)</dom>|sg) {
	my $domContents = $1;
	next unless $domContents =~ m|<position>(\d+)</position>.*?<mainBoardId>(.+?)</mainBoardId>.*?<name>(.+?)</name>.*?<productionId>(.+?)</productionId>|s;
	my ($pos, $mbid, $name, $prod) = ($1, $2, $3, $4);
	# print "$stringNum-$pos $mbid $name $prod\n";
	push @ddDoms, $mbid;
	$ddStringOf{$mbid} = $stringNum;
	$ddPosOf   {$mbid} = $pos;
	$ddNameOf  {$mbid} = $name;
	$ddProdOf  {$mbid} = $prod;
	$ddIsNew   {$mbid} = 0;
	if($domContents =~ m|<xCoordinate>(.+?)</xCoordinate>.*?<yCoordinate>(.+?)</yCoordinate>.*?<zCoordinate>(.+?)</zCoordinate>|s) {
	    $ddxof{$mbid} = $1;
	    $ddyof{$mbid} = $2;
	    $ddzof{$mbid} = $3;
	    $strPosToX{"$stringNum,$pos"} = $1;
	    $strPosToY{"$stringNum,$pos"} = $2;
	    $strPosToZ{"$stringNum,$pos"} = $3;
	    # print "$xof{$mbid} $yof{$mbid} $zof{$mbid}\n";
	} else {
	    $ddxof{$mbid} = undef;
	    $ddyof{$mbid} = undef;
	    $ddzof{$mbid} = undef;
	}

	$inGeom{$mbid} = 1; # Mark as found
    }
}

my @domsToAdd;
# Find DOMs not in deployed list:
foreach my $mb (@mbids) {
    if(!$inGeom{$mb}) {
	# printf "%02d-%02d %s (%s)\n", $stringof{$mb}, $posof{$mb}, $mb, $nameof{$mb};
	push @domsToAdd, $mb;
    }
}

my $nToAdd = @domsToAdd;
#print "Will add $nToAdd DOMs.\n";

foreach my $mb(@domsToAdd) {  # Translate to geometry dataset
    push @ddDoms, $mb;
    $ddStringOf{$mb} = $stringof{$mb};
    $ddPosOf   {$mb} = $posof{$mb};
    $ddNameOf  {$mb} = $nameof{$mb};
    $ddProdOf  {$mb} = $domidof{$mb};
    $ddIsNew   {$mb} = 1;
    # Get position from simulation if needed
    if(!defined $ddxof{$mb}) {
	#printf "Filling position from simulation (%d,%d)...\n", 1000+$stringof{$mb},$posof{$mb};
	my $x = $strPosToX{sprintf("%d,%d",1000+$stringof{$mb},$posof{$mb})};
	my $y = $strPosToY{sprintf("%d,%d",1000+$stringof{$mb},$posof{$mb})};
	my $z = $strPosToZ{sprintf("%d,%d",1000+$stringof{$mb},$posof{$mb})};
	if(defined $x && defined $y && defined $z) {
	    $ddxof{$mb} = $x;
	    $ddyof{$mb} = $y;
	    $ddzof{$mb} = $z;
	    #print "$x, $y, $z\n";
	}
    }
}

# Sort DOM list by string and position:
sub byStringAndPos { 
    if($ddStringOf{$a} == $ddStringOf{$b}) {
	return $ddPosOf{$a} <=> $ddPosOf{$b};
    } else {
	return $ddStringOf{$a} <=> $ddStringOf{$b};
    }
}
@ddDoms = sort byStringAndPos @ddDoms;

print <<EOH;
<?xml version="1.0"?>
<domGeometry>
EOH
    ;
my $lastString;

foreach my $mb(@ddDoms) {
    #printf("%02d-%02d%s %s (%s) ", 
    #  $ddStringOf{$mb}, $ddPosOf{$mb}, $ddIsNew{$mb}?"**":"",
    #  $mb, $ddNameOf{$mb});
    if(!defined $lastString) {
	printf "   <string>\n      <number>%02d</number>\n", $ddStringOf{$mb};
    } elsif($lastString != $ddStringOf{$mb}) {
	printf "   </string>\n   <string>\n      <number>%02d</number>\n", $ddStringOf{$mb};
    }
    $lastString = $ddStringOf{$mb};
    print <<EOD;
      <dom>
         <position>$ddPosOf{$mb}</position>
         <mainBoardId>$mb</mainBoardId>
         <name>$ddNameOf{$mb}</name>
         <productionId>$ddProdOf{$mb}</productionId>
EOD
;
    my $coords = "";
    if(defined $ddxof{$mb} && defined $ddyof{$mb} && defined $ddzof{$mb}) {
	$coords =<<EOC;
         <xCoordinate>$ddxof{$mb}</xCoordinate>
         <yCoordinate>$ddyof{$mb}</yCoordinate>
         <zCoordinate>$ddzof{$mb}</zCoordinate>
EOC
;
    }
    print "$coords      </dom>\n";
}

print "   </string>\n</domGeometry>\n";


__END__

