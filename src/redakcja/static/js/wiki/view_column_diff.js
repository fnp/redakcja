(function($){

    class DiffPerspective extends $.wiki.Perspective {
        constructor(options) {
            super(options);
            this.base_id = options.base_id;
        }

        static openId(id) {
            let match = id.match(/R(\d+)-(\d+)/);
            if (!match)
                return [];
            return this.open(match[1], match[2]);
        }

        static open(revFrom, revTo) {
            let tabId = 'R' + revFrom + '-' + revTo;
            let tab = $(".tabs #DiffPerspective_" + tabId);
            if (tab.length) {
                $.wiki.switchToTab(tab);
            } else {
                let result = $.wiki.newTab(CurrentDocument, ''+revFrom +' &rarr; ' + revTo, 'DiffPerspective', tabId);
                $.blockUI({
                    message: 'Wczytywanie porównania...'
                });

                CurrentDocument.fetchDiff({
                    from: revFrom,
                    to: revTo,
                    success: function(doc, data){
                        $(result.view).html(data);
                        $.wiki.switchToTab(result.tab);
                        $.unblockUI();
                    },
                    failure: function(doc){
                        $.unblockUI();
                    }
                });
                return result.tab;
            }
        }

        destroy() {
            $.wiki.switchToTab('#HistoryPerspective');
            $('#' + this.base_id).remove();
            $('#' + this.perspective_id).remove();
        }
    }
    $.wiki.DiffPerspective = DiffPerspective;

})(jQuery);
