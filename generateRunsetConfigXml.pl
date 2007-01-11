#!/usr/bin/perl

# gen10str
# John Jacobsen, NPX Designs, Inc., jacobsen\@npxdesigns.com
# Started: Thu Jan 11 13:05:32 2007


use strict;

my $geomxml = "default-dom-geometry.xml";
#my @strings = (1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010);
my $minString = 1001;
my $numStrings = shift;
$numStrings = 1 unless defined $numStrings;
$numStrings = 1 unless $numStrings > 0;
my $maxString = 1001+$numStrings-1;
my @strings;
for($minString..$maxString) { push @strings, $_; }

open(F, $geomxml) or die "Can't.";
my $xml;
while(<F>) {
    $xml .= $_;
}

sub inList { 
    my $what = shift;
    my @array = @_;
    for(@array) {
	return 1 if $what == $_;
    }
    return 0;
}

print "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
print "<domConfigList configId=\"1000002\">\n";

open(NAMES, "names.txt") or die "Can't.";

while($xml =~ /<string>(.+?)<\/string>/sg) {
    my $strPat = $1;
    next if $strPat !~ /<number>(\d+)<\/number>/;
    my $strNum = $1;
    if(inList($strNum, @strings)) {
	while($strPat =~ /<dom>(.+?)<\/dom>/sg) {
	    my $domPat = $1;
	    my $mbid;

	    if($domPat =~ /<mainBoardId>(\S+?)<\/mainBoardId>/) {
		$mbid = $1;
	    } else { next; }

	    my $name = <NAMES>; 
	    chomp $name;   
	    print <<EOF;
    <domConfig mbid="$mbid" name="$name">
        <simulation>
            <noiseRate>50.0</noiseRate>
        </simulation>
    </domConfig>
EOF
;
	}
    }
}

print "</domConfigList configId=\"1000003\">\n";

__END__

