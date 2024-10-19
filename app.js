$('#auth_form').submit(function(e) {
	e.preventDefault();
	if ($('[name="user_login"]').val() && $('[name="user_password"]').val()) {
		$('[name="user_login"]').css('border', '1px solid #b3b3b3');
		$('[name="user_password"]').css('border', '1px solid #b3b3b3');
		$.ajax({
			url: 'login',
			type: 'POST',
			dataType: 'json',
			data: $(this).serialize(),
			success: function(data) { alert("Да, брат, есть такой"); },
			error: function(err) { alert("Сорян, брат, такого нет"); }
		});
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
