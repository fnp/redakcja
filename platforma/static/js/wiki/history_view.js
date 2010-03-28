(function($){

    function fetchDiff(success, failed){
        var changelist = $('#changes-list');
   
		var selected = $('div.selected', changelist); 
        
        if (selected.length != 2) {
            window.alert("Musisz zaznaczyć dokładnie dwie wersje do porównania.");
            if(failed) failed();
        }
        
        $.blockUI({
            message: 'Wczytywanie porównania...'
        });
        
        $.ajax({
			method: "GET",
            url: document.location.href + '/diff/' + rev_a.val() + '/' + rev_b.val(),
            dataType: 'html',
            error: function(){
                $.unblockUI();
                if(failed) failed('Nie udało się wczytać porównania z serwera.');
            },
            success: function(data){
                var diffview = $('#diff-view');
                diffview.html(data);
                diffview.show();
                $.unblockUI();
                if(success) success(data);
            }
        });
    }
    
    function HistoryPerspective(doc, callback) {
		this.perspective_id = 'HistoryPerspective';
		this.doc = doc;
		
        // first time page is rendered
        $('#make-diff-button').click(fetchDiff);
		
		$('#changes-list div').live('click', function() {
			var $this = $(this);
			if($this.hasClass('selected')) 
				return $this.removeClass('selected');
				
			if($("#changes-list div.selected").length < 2)
				return $this.addClass('selected');
		});
		
		$('#changes-list span.tag').live('click', function(event) {			
			return false;						
		});
		
		callback.call(this);
    };
    
    HistoryPerspective.prototype = new $.wiki.Perspective();
    
    HistoryPerspective.prototype.freezeState = function(){
        // must 
    };
    
    HistoryPerspective.prototype.onEnter = function(success, failure) 
	{		
		$.wiki.Perspective.prototype.onEnter.call(this);
		
        $.blockUI({
            message: 'Odświeżanie historii...'
        });
		
		function _finalize(s) {
			$.unblockUI();
			
			if(s) { if(success) success(); }
			else { if(failure) failure(); }
		}
        
        function _failure(doc, message) {
          $('#history-view .message-box').html('Nie udało się odświeżyć historii:' + message).show();
		  _finalize(false);    
        };
          
		function _success(doc, data) {
        	$('#history-view .message-box').hide();
            var changes_list = $('#changes-list');
            var $stub = $('#history-view .row-stub');                
            changes_list.html('');
                
            $.each(data, function(){
            	$.wiki.renderStub(changes_list, $stub, this);								
            });
			
			$('span[data-version-tag]', changes_list).each(function() {
				$(this).text($(this).attr('data-version-tag'));				
			});
			
			_finalize(true);			
        };
		
		return this.doc.fetchHistory({success: _success, failure: _failure});
    };    
		
	$.wiki.HistoryPerspective = HistoryPerspective;
	
})(jQuery);
