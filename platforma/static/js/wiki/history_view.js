(function($){
    
    function HistoryPerspective(options) {
		var old_callback = options.callback || function() {};
		
		options.callback = function() {
			var self = this;
			
			// first time page is rendered
        	$('#make-diff-button').click(function() {
				self.makeDiff();
			});
			
			$('#tag-changeset-button').click(function() {
				self.showTagForm();				
			});
        
        	$('#changes-list .entry').live('click', function(){
            	var $this = $(this);
            	if ($this.hasClass('selected')) 
                	return $this.removeClass('selected');
            
            	if ($("#changes-list .entry.selected").length < 2) 
                	return $this.addClass('selected');
        	});
	        
    	    $('#changes-list span.tag').live('click', function(event){
        	    return false;
        	});
        
        	old_callback.call(this);
		}
		
		$.wiki.Perspective.call(this, options);		
    };
    
    HistoryPerspective.prototype = new $.wiki.Perspective();
    
    HistoryPerspective.prototype.freezeState = function(){
        // must 
    };
    
    HistoryPerspective.prototype.onEnter = function(success, failure){
        $.wiki.Perspective.prototype.onEnter.call(this);
        
        $.blockUI({
            message: 'Odświeżanie historii...'
        });
        
        function _finalize(s){
            $.unblockUI();
            
            if (s) {
                if (success) 
                    success();
            }
            else {
                if (failure) 
                    failure();
            }
        }
        
        function _failure(doc, message){
            $('#history-view .message-box').html('Nie udało się odświeżyć historii:' + message).show();
            _finalize(false);
        };
        
        function _success(doc, data){
            $('#history-view .message-box').hide();
            var changes_list = $('#changes-list');
            var $stub = $('#history-view .row-stub');
            changes_list.html('');
            
            $.each(data, function(){
                $.wiki.renderStub(changes_list, $stub, this);
            });
            
            $('span[data-version-tag]', changes_list).each(function(){
                $(this).text($(this).attr('data-version-tag'));
            });
            
            _finalize(true);
        };
        
        return this.doc.fetchHistory({
            success: _success,
            failure: _failure
        });
    };
	
	HistoryPerspective.prototype.showTagForm = function(){
		var selected = $('#changes-list .entry.selected');
		
		if (selected.length != 1) {
            window.alert("Musisz dokładnie jedną wersję do oznaczenia.");            
            return;
        }
		
		var version = parseInt($("*[data-stub-value='version']", selected[0]).text());
		var dialog = $('#add_tag_dialog');
		
		$("input[name='version']", dialog).val(version);
		
		console.log($('form', dialog).serialize());
		
		$.blockUI({
			message: dialog
		});
	};
	
	HistoryPerspective.prototype.makeDiff = function() {
        var changelist = $('#changes-list');        
        var selected = $('.entry.selected', changelist);
        
        if (selected.length != 2) {
            window.alert("Musisz zaznaczyć dokładnie dwie wersje do porównania.");            
            return;
        }
        
        $.blockUI({
            message: 'Wczytywanie porównania...'
        });
		
		var rev_from = $("*[data-stub-value='version']", selected[1]).text();
		var rev_to =  $("*[data-stub-value='version']", selected[0]).text();
        
        return this.doc.fetchDiff({
            from: rev_from, 
			to: rev_to,            
            success: function(doc, data){
                var result = $.wiki.newTab(doc, ''+rev_from +' -> ' + rev_to, 'DiffPerspective');
				
				$(result.view).html(data);
				$.wiki.switchToTab(result.tab);	
				$.unblockUI();
            },
            failure: function(doc){
                $.unblockUI();
            }
        });
    };
    
    $.wiki.HistoryPerspective = HistoryPerspective;
    
})(jQuery);
