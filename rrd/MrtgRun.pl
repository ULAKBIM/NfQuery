#!/usr/bin/perl


use ConfigUtils 'parseConfigFile';
use Logger 'logger';

use strict;

my $cfg = &parseConfigFile();

my $mrtg = $cfg->param('MRTG');


sub runMrtg{
	
	my $type = shift;
	
	my $mrtg_conf_path = $cfg->param('MRTG_CONF_PATH') . "/$type";
	my $mrtg_work_dir = $cfg->param('MRTG_WORK_DIR') . "/$type";

	unless(-d $mrtg_work_dir){
		    mkdir $mrtg_work_dir or logger('info', "Cannot create $mrtg_conf_path dir");
	}



	opendir MRTG_CONFDIR, $mrtg_conf_path;

	while (my $config_file = readdir(MRTG_CONFDIR)){

		#Find .cfg files in MRTG_CONF_PATH and run mrtg.
	
		if ($config_file =~ /.cfg$/){
	
			logger('info', "Running $config_file");
			my @output = `($mrtg  $mrtg_conf_path/$config_file 2>&1 )`;
		
			chop(@output);
			foreach my $line (@output){
				 logger('info', " -$line");
			}

		}
	}

}

#############################################
#				RUN MRTG (pps, bps)			#
#############################################

&runMrtg('bps');
&runMrtg('pps');

