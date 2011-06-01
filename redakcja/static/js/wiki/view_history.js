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

	        $('#doc-revert-button').click(function() {
	            self.revertDialog();
	        });

			$('#open-preview-button').click(function(event) {
				var selected = $('#changes-list .entry.selected');

				if (selected.length != 1) {
        		    window.alert("Wybierz dokładnie *jedną* wersję.");
            		return;
		        }

				var version = parseInt($("*[data-stub-value='version']", selected[0]).text());
				window.open($(this).attr('data-basehref') + "?revision=" + version);

				event.preventDefault();
			});

        	$('#changes-list .entry').live('click', function(){
            	var $this = $(this);

            	var selected_count = $("#changes-list .entry.selected").length;

            	if ($this.hasClass('selected')) {
                	$this.removeClass('selected');
                	selected_count -= 1;
            	}
            	else {
            	    if (selected_count  < 2) {
            	        $this.addClass('selected');
            	        selected_count += 1;
            	    };
            	};

            	$('#history-view-editor .toolbar button').attr('disabled', 'disabled').
            	    filter('*[data-enabled-when~=' + selected_count + '], *[data-enabled-when~=*]').
            	    attr('disabled', null);
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

			var tags = $('select#id_addtag-tag option');

            $.each(data, function(){
                $.wiki.renderStub({
					container: changes_list,
					stub: $stub,
					data: this,
					filters: {
//						tag: function(value) {
//							return tags.filter("*[value='"+value+"']").text();
//						}
//                        description: function(value) {
//						    return value.replace('\n', ');
//						}
					}
				});
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
            window.alert("Musisz zaznaczyć dokładnie jedną wersję.");
            return;
        }

		var version = parseInt($("*[data-stub-value='version']", selected[0]).text());
		$.wiki.showDialog('#add_tag_dialog', {'revision': version});
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

    HistoryPerspective.prototype.revertDialog = function(){
        var self = this;
        var selected = $('#changes-list .entry.selected');

        if (selected.length != 1) {
            window.alert("Musisz zaznaczyć dokładnie jedną wersję.");
            return;
        }

        var version = parseInt($("*[data-stub-value='version']", selected[0]).text());
        $.wiki.showDialog('#revert_dialog', {revision: version});
    };

    $.wiki.HistoryPerspective = HistoryPerspective;

})(jQuery);
