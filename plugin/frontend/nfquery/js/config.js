function register(){
	$("#warning").empty();
	if(!$("#id_plugin_ip").val() || !$("#id_queryserverip").val() || !$("#id_queryserverport").val() ||
	 !$("#id_pkeyfile").val()){
		$("#warning").attr("class","alert alert-error");
		$('#warning').append("Fill all field");
	}
	else{
		 $("#warning").attr("class","");
		 $("#warning").empty();
		 var map = {'plugin_ip':$("#id_plugin_ip").val(),'qserver_ip':$("#id_queryserverip").val(),
			    'qserver_port':$("#id_queryserverport").val(),
				'publickeyfile':$("#id_pkeyfile").val()};
		$.post("/nfsen/plugins/nfquery/ajaxhandler.php",{map:map},function(data){
			window.location.reload();
		});	 
	}
}

//	if(!$("#id_organization").val()){kontrol=0;
//		$("#orgdiv").attr("class",error_class);
//	}else{$("#orgdiv").attr("class","");kontrol=1;}
//	if(!$("#id_admin_name").val()){
//		$("#admin_name_div").attr("class",error_class);
//	}else{$("#admin_name_div").attr("class","");}
//	if(!$("#id_admin_email").val()){
//		$("#admin_mail_div").attr("class",error_class);
//	}else{$("#admin_mail_div").attr("class","");}
//	if(!$("#id_admin_phone").val()){
//		$("#id_admphone_div").attr("class",error_class);
//	}else{$("#id_admphone_div").attr("class","");}
//	if(!$("#id_plugin_ip").val()){
//		$("#id_plugin_div").attr("class",error_class);
//	}else{$("#id_plugin_div").attr("class","");}
//	if(!$("#id_prefix").val()){
//		$("#id_prefix_div").attr("class",error_class);
//	}else{$("#id_prefix_div").attr("class","");}
//	if(!$("#id_queryserverip").val()){
//		$("#id_queryserver_div").attr("class",error_class);
//	}else{$("#id_queryserver_div").attr("class","");}
//	if(!$("#id_queryserverport").val()){
//		$("#id_qsport_div").attr("class",error_class);
//	}else{$("#id_qsport_div").attr("class","");}

