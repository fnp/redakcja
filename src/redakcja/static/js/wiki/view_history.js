(function($){

    function HistoryPerspective(options) {
	var old_callback = options.callback || function() {};

	options.callback = function() {
	    var self = this;
            if (CurrentDocument.diff) {
                rev_from = CurrentDocument.diff[0];
                rev_to = CurrentDocument.diff[1];
                this.doc.fetchDiff({
                    from: rev_from,
                    to: rev_to,
                    success: function(doc, data){
                        var result = $.wiki.newTab(doc, ''+rev_from +' -> ' + rev_to, 'DiffPerspective');

                        $(result.view).html(data);
                        $.wiki.switchToTab(result.tab);
                    }
                });
            }

	    // first time page is rendered
            $('#make-diff-button').click(function() {
		self.makeDiff();
	    });

	    $('#pubmark-changeset-button').click(function() {
		self.showPubmarkForm();
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

            $(document).on('click', '#changes-list .entry', function(){
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
                    filter('*[data-enabled-when~="' + selected_count + '"]').
            	    attr('disabled', null);
            });

            $(document).on('click', '#changes-list span.tag', function(event){
                return false;
            });

            $('#history-view').on('scroll', function() {
                if (self.finished || self.fetching) return;
                var elemTop = $('#history-view .message-box').offset().top;
                var windowH = $(window).innerHeight();
                if (elemTop - 20 < windowH) {
                    self.triggerFetch();
                }
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
        this.startFetching();
        success && success();
    };

    HistoryPerspective.prototype.startFetching = function() {
        $('#history-view .message-box').html('Wczytywanie historii…').show();
        $('#changes-list').html('');
        this.finished = false;
        this.before = '';
        this.triggerFetch();
    };
    HistoryPerspective.prototype.stopFetching = function() {
        self.finished = true;
        $('#history-view .message-box').hide()
    };


    HistoryPerspective.prototype.triggerFetch = function() {
        var self = this;
        self.fetching = true;

        function _finalize() {
            self.fetching = false;
        }

        function _failure(doc, message){
            $('#history-view .message-box').html('Nie udało się odświeżyć historii:' + message).show();
            _finalize();
        };

        function _success(doc, data){
            //$('#history-view .message-box').hide(); ONLY AFTER LAST!
            var changes_list = $('#changes-list');
            var $stub = $('#history-view .row-stub');

            if (!data.length) {
                self.stopFetching();
            }

            $.each(data, function(){
                $.wiki.renderStub({
		    container: changes_list,
		    stub: $stub,
		    data: this,
		});
                self.before = this.version;
                if (this.version == 1) {
                    self.stopFetching();
                }
            });

            _finalize();
        };

        this.doc.fetchHistory({
            success: _success,
            failure: _failure,
            before: this.before,
        });
    }


	HistoryPerspective.prototype.showPubmarkForm = function(){
		var selected = $('#changes-list .entry.selected');

		if (selected.length != 1) {
            window.alert("Musisz zaznaczyć dokładnie jedną wersję.");
            return;
        }

		var version = parseInt($("*[data-stub-value='version']", selected[0]).text());
		$.wiki.showDialog('#pubmark_dialog', {'revision': version});
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
