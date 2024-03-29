(function($){

    class HistoryPerspective extends $.wiki.Perspective {
        constructor(options) {
            super(options);
            var self = this;

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

            $(document).on('click', '#changes-list .entry .approved', function(){
                $("#changes-list .entry.selected").removeClass('selected');
                $(this).closest('.entry').click();
                self.showPubmarkForm();
                return false;
            })
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
        }

        onEnter(success, failure) {
            super.onEnter();
            this.startFetching();
            success && success();
        }

        startFetching() {
            $('#history-view .message-box').html('Wczytywanie historii…').show();
            $('#changes-list').html('');
            this.finished = false;
            this.before = '';
            this.triggerFetch();
        }
        stopFetching() {
            self.finished = true;
            $('#history-view .message-box').hide()
        }

        triggerFetch() {
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

        showPubmarkForm() {
            var selected = $('#changes-list .entry.selected');

            if (selected.length != 1) {
                window.alert("Musisz zaznaczyć dokładnie jedną wersję.");
                return;
            }

            var version = parseInt($("*[data-stub-value='version']", selected[0]).text());
            var approved = selected.attr('data-approved') == 'true';
            $.wiki.showDialog('#pubmark_dialog', {'revision': version, 'approved': !approved});
        }

        makeDiff() {
            var changelist = $('#changes-list');
            var selected = $('.entry.selected', changelist);

            if (selected.length != 2) {
                window.alert("Musisz zaznaczyć dokładnie dwie wersje do porównania.");
                return;
            }

            var rev_from = $("*[data-stub-value='version']", selected[1]).text();
            var rev_to =  $("*[data-stub-value='version']", selected[0]).text();

            $.wiki.DiffPerspective.open(rev_from, rev_to);
        }

        revertDialog() {
            var self = this;
            var selected = $('#changes-list .entry.selected');

            if (selected.length != 1) {
                window.alert("Musisz zaznaczyć dokładnie jedną wersję.");
                return;
            }

            var version = parseInt($("*[data-stub-value='version']", selected[0]).text());
            $.wiki.showDialog('#revert_dialog', {revision: version});
        }
    }
    $.wiki.HistoryPerspective = HistoryPerspective;

})(jQuery);
