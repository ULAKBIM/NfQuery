#!/usr/bin/perl

use ConfigUtils 'parseConfigFile';
use Webservice  'getLinksOfManIp';
use Logger 'logger';

use strict;


my $cfg = &parseConfigFile();
my $mrtg_conf_path = $cfg->param('MRTG_CONF_PATH') . "/pps";
my $mrtg_work_dir = $cfg->param('MRTG_WORK_DIR');

unless(-d $mrtg_conf_path){
	    mkdir $mrtg_conf_path or logger('info', "Cannot create $mrtg_conf_path dir");
}

my %man_links = &getLinksOfManIp();

&logger('info', 'Mrth Config File Generator is Running Now');

foreach my $man_ip (keys %man_links){
	my %links = %{$man_links{$man_ip}};
	
	my $config_file = $mrtg_conf_path."/".$man_ip."_pps.cfg";

	open FILE, ">:utf8", "$config_file" or logger('err', "Connot create $config_file");
	flock FILE, 2;
	
	print FILE "WorkDir: $mrtg_work_dir/pps\n";
	print FILE "WriteExpires: Yes\n";
	print FILE "IconDir: ./\n";
	print FILE "Language: english\n";
	print FILE "Options[_]: nopercent, growright\n";
	print FILE "YLegend[_]: Paket/Saniye\n";
	print FILE "Refresh: 300\n";
	print FILE "Interval: 5\n";
	print FILE "LogFormat: rrdtool\n";
	print FILE "PathAdd: /usr/local/bin\n";
	print FILE "EnableSnmpV3: yes\n\n\n";
	
	&logger('info', "Creating $man_ip.cfg");

	foreach my $link_id (keys %links){
		my %link = %{$links{$link_id}};
		my $byte_speed = int($link{'link_speed'}) * 1000000 / 8;
	
		printf FILE "#----------------------------------%s----------------------------------\n", $link{'inst_name'};

        printf FILE "Target[%s-%s-pps]: ifInUcastPkts.%s&ifOutUcastPkts.%s:public@%s:::::3\n", 
			$link{'inst_code'}, $link{'link_id'}, $link{'router_ifindex'}, $link{'router_ifindex'}, $link{'router_man_ip'};

        printf FILE "SnmpOptions[%s-%s-pps]: username=>'istatistik'\n", $link{'inst_code'}, $link{'link_id'};
        printf FILE "MaxBytes[%s-%s-pps]: %s\n", $link{'inst_code'}, $link{'link_id'}, 2500000000;
        printf FILE "Title[%s-%s-pps]: ULAKNET - %s (%s Mbps)\n", $link{'inst_code'}, $link{'link_id'}, $link{'inst_name'}, $link{'link_speed'};
	    printf FILE "PageTop[%s-%s-pps]: <H4>%s (%s Mbps) Kullanım İstatistikleri</H4>", $link{'inst_code'}, $link{'link_id'}, $link{'inst_name'}, $link{'link_speed'};
		
		print  FILE " <HR WIDTH=\"100%\">\n";
		print  FILE " Burada görülen istatistikler\n";
		print  FILE " ULAKNET ana yönlendirilicileri üzerindeki arayüzlerden alinmaktadir.";
		print  FILE " <FONT COLOR=\"#33FF33\">Yeşil</FONT> renk ULAKNET'ten\n";
		print  FILE " Kullanıcıya doğru giden trafiği gösterir. <FONT COLOR=\"#3333FF\">Mavi</FONT>\n";
		print  FILE " renk ise Kullanicidan ULAKNET'e dogru giden trafigi göstermekte. Herhangi\n";
		print  FILE " bir soru veya sorun var ise lütfen <A HREF=\"mailto:noc\@ulakbim.gov.tr\">noc\@ulakbim.gov.tr</A>\n";
		print  FILE " adresine e-mail ile bildirin.\n";
		print  FILE " <BR>\n";
		print  FILE " <HR WIDTH=\"100%\">\n";
		
		print  FILE " <TABLE>\n";
		printf FILE	" <TR><TD>Sistem:</TD><TD>%s</TD></TR>\n", $link{'inst_name'}; 
		printf FILE	" <TR><TD>Kart:</TD><TD>%s</TD></TR>\n", $link{'interface'}; 
		printf FILE	" <TR><TD>Hız:</TD><TD>%s Mbps</TD></T>\n", $link{'link_speed'}; 
		print  FILE " </TABLE>\n";
		print  FILE "#-----------------------------------------------------------------------\n\n";
	}

	close FILE;
}

&logger('info', "Mrtg Configuration Files Created Successfuly");

