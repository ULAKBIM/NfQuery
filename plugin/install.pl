#!/usr/bin/env perl

use strict;
use File::Basename;
use Cwd;
use Getopt::Std;


my @nfsen_search_paths = ("/usr/local/bin/nfsen", "/data/nfsen/bin/nfsen", "/usr/bin/nfsen");
my $nfsen_path;
my $module_dir;
my $plugin_path;
our $opt_h;
my $backup_suffix = "-uninstalled.at-".`date +"%Y.%m.%d-%H.%M.%S"`;
chop $backup_suffix;

my @module_dependency = (
	"Digest::MD5",
	"JSON",
	"JSON::RPC::LWP",
	"NetAddr::IP",
	"Net::SSL",
	"Parallel::ForkManager",
	"DBM::Deep",
	"LWP::UserAgent",
);

my @missing_modules = ();

################################################################################
sub usage {
	print	"$0 [-h] [full_path_of_nfsen]\n",
		"\t-h This help\n",
		"\n", 
		"",
		"Eg: $0 /usr/local/bin/nfsen",
		"\n";
}

################################################################################
sub installFile {
	my $from = shift;
	my $to = shift;
	my $rp;

	if ( -e "$to") {
		if ((-l "$to") && ($rp = readlink($to)) && ($from eq Cwd::abs_path($rp))) {
#SIL#			print "from: $from to: $to\n";
#SIL#			print "$rp\n";
#SIL#			print Cwd::abs_path($rp). "\n";
			print "$from is already installed\n";
			return (1);
		} else {
#SIL#			print "from: $from to: $to\n";
#SIL#			print "$rp\n";
#SIL#			print Cwd::abs_path($rp). "\n";
			print "Backing up the old installation file $to as $to$backup_suffix\n";
			rename ($to, $to.$backup_suffix);
		}
	}
	print "Installing new file: $from $to\n";
	symlink ($from, $to);
	return (1);
}

################################################################################
################################################################################
################################################################################
if ($> != 0) {
	print "$0 should be run as root!\n";
	exit 3;
}

getopts('h');

if ($opt_h) {
	usage();
	exit;
}

foreach my $m (@module_dependency) {
	eval "require $m" or push @missing_modules, $m
}

if (@missing_modules) {
	print "The following Perl Modules are missing:\n\t";
	print join("\n\t", @missing_modules) . "\n";
	print "Please install the missing Perl Modules either via your Unix distro's package manager or via perl cpan shell. And then install NfQuery plugin.\n";
	exit 4;
}

if (@ARGV) {
	unshift @nfsen_search_paths, $ARGV[0];
}

foreach my $p (@nfsen_search_paths) {
	print "Checking nfsen file: $p\n";
	$nfsen_path = $module_dir = "";
	if ( -f $p && -r $p) {
		$nfsen_path = $p;
		if ($module_dir = `grep "^use lib" $nfsen_path | head -1 | cut -d '"' -f 2 `) {
			chop $module_dir;
			print "\tFound '$module_dir' as NfSen LIBEXEC dir.\n";
			if (! -d $module_dir) {
				print "\t'$module_dir' is not a directory.\n";
				next;
			} elsif (! -f "$module_dir/NfConf.pm") {
				print "\tNfConf.pm cannot be found under '$module_dir'\n";
				next;
			}
			last;
		} else {
			print "\tNfSen module dir cannot be found!\n";
		}
	} else {
		print "\t'$p' doesnot exist!\n"
	}
}

if ("x$module_dir" eq "x") {
	die	"\nnfsen not found!\n",
		"Please feed full path of nfsen to this script as:\n\n",
		"\t$0 path_to_nfsen\n",
		"\n";
}

print "\n";

$plugin_path = Cwd::abs_path(dirname($0));

unshift @INC, $module_dir;
eval {
	require NfConf;
} or die "An error occurred while loading NfConf module: '$@'. Exiting.\n";

NfConf::LoadConfig() or die "Couldn't load NfSen Config. Exiting.\n";

print "BACKEND_PLUGINDIR: $NfConf::BACKEND_PLUGINDIR\n";
print "FRONTEND_PLUGINDIR: $NfConf::FRONTEND_PLUGINDIR\n";
print "WWWUSER: $NfConf::WWWUSER\n";
print "WWWGROUP: $NfConf::WWWGROUP\n";
print "plugin_path: $plugin_path\n";

# install backend files;
installFile("$plugin_path/backend/nfquery.pm", "$NfConf::BACKEND_PLUGINDIR/nfquery.pm") or die;

# install frontend files;
installFile("$plugin_path/frontend/nfquery.php", "$NfConf::FRONTEND_PLUGINDIR/nfquery.php") or die;
installFile("$plugin_path/frontend/nfquery", "$NfConf::FRONTEND_PLUGINDIR/nfquery") or die;

print "NfQuery is successfully installed.\n";
print "Baalsasasa conf dosyasi\n";
