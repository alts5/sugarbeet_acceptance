var pathToBackend = window.location.hostname;

function getUser() {
	var f = null;
	$.ajax({
		'async': false,
		url: 'http://' + pathToBackend + ':8000/user-info',     
		method: 'GET',
		dataType: 'json',
		headers: {token : sessionStorage.getItem("token")}, 
		success: function(data){
			f = data;
		},
	});
	return f;
}

