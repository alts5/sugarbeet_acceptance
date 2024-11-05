var pathToBackend = window.location.hostname;

$('#auth_form').submit(function(e) {
	e.preventDefault();
	checkEmptyFieldsInForm('auth_form');
	if ($('[name="user_login"]').val() && $('[name="user_password"]').val()) {
        errorInformController(0);

		$.ajax({
			url: 'http://' + pathToBackend + ':8000/authenticate',     
			method: 'POST',
			dataType: 'json',
			contentType: "application/x-www-form-urlencoded",
			data: $(this).serialize(),
			success: function(data){
				errorInformController(0)
				sessionStorage.setItem('token', data["token"]);
				window.location.href="/workroom.html";
			},
			error: function(data, response){
				if (response.status == 403) errorInformController(1, "Неверный логин или пароль")
				else errorInformController(1, "Произошла внутренняя ошибка")
			}
		});
	}
	return false;
});

function checkEmptyFieldsInForm(formId) {
    $('#' + formId +' *').filter('input').each(function(){
			if ($(this).val()) $(this).css('border', '1px solid #b3b3b3');
			else $(this).css('border', '1px solid #ed1e36');
	});
}

function errorInformController(action, error = "") {
    if (action == 1 && $('.error_base').css("display") == "none") {
        $('.modal_window').height($('.modal_window').height() + $('.error_base').height() + 10);
        $('.error_base').text(error).css("display", "block");
    }
    else {
        if ($('.error_base').css("display") == "block") {
            $('.modal_window').height($('.modal_window').height() - $('.error_base').height() - 10);
            $('.error_base').css("display", "none");
        }
    }
}

function modal_window_controller(elem, action) {
	if (action == 1) {
		$('.modal_wrap_lk').css("display", "block");
		$('#' + elem).css("display", "block");
	}
	else {
		$('.modal_wrap_lk').css("display", "none");
		$('#' + elem).css("display", "none");
	}
}

$(document).ready(function() {
	$('.dateMask').mask('99.99.9999');
	var hrefs = {
		"Дашборд" : "../workroom", 
		"Транспортные единицы" : "../te", 
		"Лаборатория" : "../lab", 
		"Площадка разгрузки" : "../unload", 
		"Взвешивание" : "../scale", 
		"Акты приёмки" : "../acts" 
		};
	
	if ($('.username_header').length) $('.username_header').text(getUser()["fio"]);
	if ($('.nav').length) {
		for (var elem in hrefs) {
			$('.nav').append('<a href = ' + hrefs[elem] + '>' + elem + '</a>');
		}
	}
	if ($('.info_block').length) {
		$.ajax({
			url: 'http://' + pathToBackend + ':8000/dashboard-indicators',     
			method: 'GET',
			dataType: 'json',
			data: { token : sessionStorage.getItem('token') },
			success: function(data){
				$('#dayAccept').text(data["dayAccept"]);
				$('#dayReject').text(data["dayReject"]);
				$('#dayScale').text(data["dayScale"]);
				$('#totalAccept').text(data["totalAccept"]);
				$('#totalReject').text(data["totalReject"]);
				$('#totalScale').text(data["totalScale"]);
			}
		});
	}
});

