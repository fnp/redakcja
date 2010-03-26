(function($){

    function fetchDiff(success, failed){
        var changelist = $('#changes-list');
        var rev_a = $("input[name='rev_from']:checked", changelist);
        var rev_b = $("input[name='rev_to']:checked", changelist);
        
        if (rev_a.length != 1 || rev_b.length != 1) {
            window.alert("Musisz zaznaczyć dwie wersje do porównania.");
            failed();
        }
        
        if (rev_a.val() == rev_b.val()) {
            window.alert("Musisz zaznaczyć dwie różne wersje do porównania.");
            failed();
        }
        
        $.blockUI({
            message: 'Wczytywanie porównania...'
        });
        
        $.ajax({
            url: document.location.href + '/diff/' + rev_a.val() + '/' + rev_b.val(),
            dataType: 'html',
            error: function(){
                $.unblockUI();
                error();
            },
            success: function(data){
                var diffview = $('#diff-view');
                diffview.html(data);
                diffview.show();
                $.unblockUI();
                success();
            }
        });
    }
    
    function HistoryPerspective(doc, callback) {
		this.perspective_id = 'HistoryPerspective';
		this.doc = doc;
		
        // first time page is rendered
        $('#make-diff-button').click(fetchDiff);
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
			
			_finalize(true);			
        };
		
		return this.doc.fetchHistory({success: _success, failure: _failure});
    };    
		
	$.wiki.HistoryPerspective = HistoryPerspective;
	
})(jQuery);
