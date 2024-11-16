var pathToBackend = window.location.hostname;

$('#auth_form').on('submit', function(e) {
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

$('#reg_form').on('submit', function(e) {
	e.preventDefault();
	$('form [name="token"]').val(sessionStorage.getItem('token'));
	$.ajax({
			url: 'http://' + pathToBackend + ':8000/add-te',     
			method: 'POST',
			dataType: 'json',
			contentType: "application/x-www-form-urlencoded",
			data: $(this).serialize(),
			success: function(data){
				window.location.reload();
			},
			error: function(data) {
				errorPushWindow(data);
			}
		});
	return false;
});

$('#reject_form').on('submit', function(e) {
	e.preventDefault();
	$('form [name="token"]').val(sessionStorage.getItem('token'));
	$('form [name="id_te"]').val();
	$.ajax({
			url: 'http://' + pathToBackend + ':8000/reject-te',     
			method: 'POST',
			dataType: 'json',
			contentType: "application/x-www-form-urlencoded",
			data: $(this).serialize(),
			success: function(data){
				window.location.reload();
			},
			error: function(data) {
				errorPushWindow(data);
			}
		});
	return false;
});

$('#accept_form').on('submit', function(e) {
	e.preventDefault();
	$('form [name="token"]').val(sessionStorage.getItem('token'));
	$('form [name="id_te"]').val();
	$.ajax({
			url: 'http://' + pathToBackend + ':8000/accept-te',     
			method: 'POST',
			dataType: 'json',
			contentType: "application/x-www-form-urlencoded",
			data: $(this).serialize(),
			success: function(data){
				window.location.reload();
			},
			error: function(data) {
				errorPushWindow(data);
			}
		});
	return false;
});

$('#distr_form').on('submit', function(e) {
	e.preventDefault();
	$('form [name="token"]').val(sessionStorage.getItem('token'));
	$('form [name="id_te"]').val();
	$.ajax({
			url: 'http://' + pathToBackend + ':8000/distr-te',     
			method: 'POST',
			dataType: 'json',
			contentType: "application/x-www-form-urlencoded",
			data: $(this).serialize(),
			success: function(data){
				window.location.reload();
			},
			error: function(data) {
				errorPushWindow(data);
			}
		});
	return false;
});

$('#labAdd_form').on('submit', function(e) {
	e.preventDefault();
	$('form [name="token"]').val(sessionStorage.getItem('token'));
	$.ajax({
			url: 'http://' + pathToBackend + ':8000/lab-add-result',     
			method: 'POST',
			dataType: 'json',
			contentType: "application/x-www-form-urlencoded",
			data: $(this).serialize(),
			success: function(data){
				window.location.reload();
			},
			error: function(data) {
				errorPushWindow(data);
			}
		});
	return false;
});

$('#scaleAdd_form').on('submit', function(e) {
	e.preventDefault();
	$('form [name="token"]').val(sessionStorage.getItem('token'));
	$.ajax({
			url: 'http://' + pathToBackend + ':8000/scale-add-result',     
			method: 'POST',
			dataType: 'json',
			contentType: "application/x-www-form-urlencoded",
			data: $(this).serialize(),
			success: function(data){
				window.location.reload();
			},
			error: function(data) {
				errorPushWindow(data);
			}
		});
	return false;
});

function errorPushWindow(msg) {
	if (msg.responseJSON) alert(msg.responseJSON["detail"]);
	else alert("При взаимодействии с сервером произошла ошибка. Проверьте поля ввода данных");
}

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

function modal_window_controller(elem, action, row=null) {
	if (action == 1) {
		$('.modal_wrap_lk').css("display", "block");
		$('#' + elem).css("display", "block");
		if ($('#' + elem + ' input[name=id_te]').length) {
			$('#' + elem + ' input[name=id_te]').val(row);
		}
	}
	else {
		$('.modal_wrap_lk').css("display", "none");
		$('#' + elem).css("display", "none");
	}
}

function exitLK() {
	sessionStorage.clear();
	window.location.reload();
}

$(document).ready(function() {
	$('.dateMask').mask('99.99.9999');
	var hrefs = {
		"Дашборд" : "../workroom", 
		"Транспортные единицы" : "../te", 
		"Лаборатория" : "../lab", 
		"Площадка разгрузки" : "../unload", 
		"Взвешивание" : "../scale", 
		"Отчётность" : "../reports" 
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
				for (var i=0; i < data["totalAgrofirms"].length; i++) {
					var day = 0;
					var day = 0;
					if (data["dayAgrofirms"] != null && data["dayAgrofirms"][i] != undefined) day = data["dayAgrofirms"][i]["summ"];					
					$('#agrofirmsStatic>tbody').append(
						"<tr><td>" + data["totalAgrofirms"][i]["vendor"] + "</td><td>" + day + "</td><td>" + data["totalAgrofirms"][i]["summ"] + "</td></tr>"
					);
				}
			},
			error: function(data) {
				$('.error_base').css("display", "block");
			}
		});
	}
	
	if ($('#teListTable').length) {
		getTElistForTable();
	}
	if ($('#labListTable').length) {
		getLablistForTable();
	}
	if ($('#scaleListTable').length) {
		getScalelistForTable()
	}
	if ($('#labAdd_form select[name="id_te"]').length) {
		getTElistUncheckedLab();
	}
	if ($('#scaleAdd_form select[name="id_te"]').length) {
		getTElistUnweightedScale();
	}
});


function getTElistForTable() {
	$.ajax({
			url: 'http://' + pathToBackend + ':8000/te-list',     
			method: 'GET',
			dataType: 'json',
			data: { token : sessionStorage.getItem('token') },
			success: function(data) {
				if (data != undefined) {
					$('#teListTable>tbody').empty();
					for (var i = 0; i < data.length; i++) {
						var te_id = data[i]["id_te"];
						var dest = data[i]["destination"] || "Ожидает распределения";
						var warnIcon = "<td></td>";
						
						if (data[i]["result"]) {
							warnIcon = "<td><img src = 'warn.svg' title = 'Результат исследования: " + data[i]["result"]+ "'></td>"
						}
						
						$('#teListTable>tbody').append(
							"<tr><td>" + te_id + "</td><td>" + data[i]["regnum"] + "</td><td>" + data[i]["vendor"] + "</td><td>" + data[i]["time"] + "</td><td>" + data[i]["characts"] + "</td><td>" + data[i]["status"] + "</td><td>" + dest + "</td>"
							+ "<td><img src = 'reject.svg' title = 'Отбраковать транспортную единицу' onclick = 'modal_window_controller(\"rejectForm_window\", 1, " +  te_id + ")'></td>"
							+ "<td><img src = 'accept.svg' title = 'Принять транспортную единицу' onclick = 'modal_window_controller(\"acceptForm_window\", 1, " +  te_id + ")'></td>"
							+ "<td><img src = 'info.svg' title = 'Распределить транспортную единицу' onclick = 'modal_window_controller(\"distrForm_window\", 1, " +  te_id + ")'></td>"
							+ warnIcon
							+ "</tr>"
						);
					}
				}
			}
		});
}

function getLablistForTable() {
	$.ajax({
			url: 'http://' + pathToBackend + ':8000/lab-list',     
			method: 'GET',
			dataType: 'json',
			data: { token : sessionStorage.getItem('token') },
			success: function(data) {
				if (data != undefined) {
					$('#labListTable>tbody').empty();
					for (var i = 0; i < data.length; i++) {
						var te_id = data[i]["id_te"];
						var prima = data[i]["prima"] || "-";
						var secondary = data[i]["secondary"] || "-";
						var user = data[i]["fio"] || "-";
						var user_final = data[i]["user_final"] || "-";
						
						$('#labListTable>tbody').append(
							"<tr><td>" + te_id + "</td><td>" + data[i]["regnum"] + "</td><td>" + prima + "</td><td>" + secondary + "</td><td>" + user + " / " + user_final + "</td><td>" + data[i]["stat"] + "</td>"
							+ "</tr>"
						);
					}
				}
			}
		});
}

setInterval(getTElistForTable, 3000);
setInterval(getLablistForTable, 3000);
setInterval(getScalelistForTable, 3000);

function getTElistUncheckedLab() {
	$.ajax({
			url: 'http://' + pathToBackend + ':8000/te-list-unchecked-lab',     
			method: 'GET',
			dataType: 'json',
			data: { token : sessionStorage.getItem('token') },
			success: function(data) {
				if (data != undefined) {
					$('#labAdd_form select[name="id_te"]').empty();
					
					for (var i = 0; i < data.length; i++) {
						var te_id = data[i]["id_te"];
						$('#labAdd_form select[name="id_te"]').append(
							"<option value = " + te_id + ">" + data[i]["regnum"] + "</option>"
						);
					}
				}
				else {
					$('#labAdd_form select[name="id_te"]').append("<option value = '' selected hidden>Выберите госрегзнак ТЕ</option>");
				}
			}
		});
}

function getTElistUnweightedScale() {
	$.ajax({
			url: 'http://' + pathToBackend + ':8000/te-list-unweighted-scale',     
			method: 'GET',
			dataType: 'json',
			data: { token : sessionStorage.getItem('token') },
			success: function(data) {
				if (data != undefined) {
					$('#scaleAdd_form select[name="id_te"]').empty();
					
					for (var i = 0; i < data.length; i++) {
						var te_id = data[i]["id_te"];
						$('#scaleAdd_form select[name="id_te"]').append(
							"<option value = " + te_id + ">" + data[i]["regnum"] + "</option>"
						);
					}
				}
				else {
					$('#scaleAdd_form select[name="id_te"]').append("<option value = '' selected hidden>Выберите госрегзнак ТЕ</option>");
				}
			}
		});
}

function getScalelistForTable() {
	$.ajax({
			url: 'http://' + pathToBackend + ':8000/scale-list',     
			method: 'GET',
			dataType: 'json',
			data: { token : sessionStorage.getItem('token') },
			success: function(data) {
				if (data != undefined) {
					$('#scaleListTable>tbody').empty();
					for (var i = 0; i < data.length; i++) {
						var te_id = data[i]["id_te"];
						var prima = data[i]["fst"] || "-";
						var secondary = data[i]["snd"] || "-";
						var user = data[i]["fio"] || "-";
						var user_final = data[i]["user_final"] || "-";
						
						$('#scaleListTable>tbody').append(
							"<tr><td>" + te_id + "</td><td>" + data[i]["regnum"] + "</td><td>" + prima + "</td><td>" + secondary + "</td><td>" + user + " / " + user_final + "</td><td>" + data[i]["stat"] + "</td>"
							+ "</tr>"
						);
					}
				}
			}
		});
}
