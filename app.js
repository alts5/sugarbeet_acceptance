var pathToBackend = window.location.hostname;

$('#auth_form').submit(function(e) {
	e.preventDefault();
	if ($('[name="user_login"]').val() && $('[name="user_password"]').val()) {
		$('[name="user_login"]').css('border', '1px solid #b3b3b3');
		$('[name="user_password"]').css('border', '1px solid #b3b3b3');

		/*--Реализация с помощью Fetch (для тренировки навыка)-*/
        fetch('http://' + pathToBackend + ':8000/authenticate', {
            method : 'POST',
            headers: {
                'Content-type' : 'application/x-www-form-urlencoded'
            },
            body : $(this).serialize()
        })
        .then(response => {
        })
		.then(data => {
		    alert("Связьс бэком есть");
		})
		.catch(error => {
		   console.log(error);
		});

		/*$.ajax({
			url: ,
			type: 'POST',
			dataType: 'json',
			data: $(this).serialize(),
			success: function(data) { alert("Да, брат, есть такой"); },
			error: function(err) { alert("Сорян, брат, такого нет"); }
		});*/

	}
	else {
		$('#auth_form *').filter('input').each(function(){
			if ($(this).val()) $(this).css('border', '1px solid #b3b3b3');
			else $(this).css('border', '1px solid #ed1e36');
		});
	}
	return false;
});

function checkEmptyFields() {

}
