function register(){
	var error = "<span class='help-inline'>Please correct the error</span>";
	var error_class="control-groups error";
	if(!$("#id_organization").val()){
		$("#orgdiv").attr("class",error_class);
		$("#orgdiv").append(error);
	}
	if(!$("#id_admin_name").val()){
		$("#admin_name_div").attr("class",error_class);
		$("#admin_name_div").append(error);
	}
	if(!$("#id_admin_email").val()){
		$("#admin_mail_div").attr("class",error_class);
		$("#admin_mail_div").append(error);
	}
	if(!$("#id_admin_phone").val()){
		$("#admin_name_div").attr("class",error_class);
		$("#admin_name_div").append(error);
	}
	if(!$("#id_plugin_ip").val()){
		$("#admin_name_div").attr("class",error_class);
		$("#admin_name_div").append(error);
	}
	if(!$("#id_prefix").val()){
		$("#admin_name_div").attr("class",error_class);
		$("#admin_name_div").append(error);
	}
	if(!$("#id_queryserverip").val()){
		$("#admin_name_div").attr("class",error_class);
		$("#admin_name_div").append(error);
	}
	if(!$("#id_queryserverport").val())(error
		$("#admin_name_div").attr("class",error_class);
		$("#admin_name_div").append(error);
	}

}
