function subscription_toggle(button){
	if ($(button).hasClass('btn-danger')){
		button.removeClass('btn-danger');
		button.addClass('btn-success');
		button.text('On');
		
	}else if(button.hasClass('btn-success')){
		button.removeClass('btn-success');
		button.addClass('btn-danger');
		button.text('Off');
	}
}

$(document).ready(function() {
	$('.subscription_toggle').click(function(){
		subscription_toggle($(this));			
	});
	if (window.location.hash != "")
		$('a[href="' + window.location.hash + '"]').click();
});
