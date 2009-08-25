$(function() 
{
	function saveToBranch(data) {
		$.log('Saving to local branch');
		var changed_panel = $('.panel-wrap.changed');

		if( changed_panel.length == 0) 
			return; /* no changes */

		if( changed_panel.length > 1)
			alert('Błąd: więcej niż jeden panel został zmodyfikowany. Nie można zapisać.');

		save_data = changed_panel.data('ctrl').saveData();

		$.ajax({
			url: location.href,
			dataType: 'json',
			success: function(data, textStatus) {
				$.log('Success:', data);
			},
			error: function(rq, tstat, err) {
			 	$.log('save error', rq, tstat, err);
			},
			type: 'POST',
			data: save_data
		});
	}
	
	$('#toolbar-button-save').click(saveToBranch);
});

