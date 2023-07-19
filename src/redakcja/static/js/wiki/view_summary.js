(function($){

    class SummaryPerspective extends $.wiki.Perspective {
        constructor(options) {
            super(options);
            var self = this;

            // first time page is rendered
            $('#summary-cover-refresh').click(function() {
                self.refreshCover();
            });
        }

        refreshCover() {
            $('#summary-cover-refresh').attr('disabled', 'disabled');
            this.doc.refreshCover({
                success: function(text) {
                    $('#summary-cover').attr('src', text);
                    $('#summary-cover-refresh').removeAttr('disabled');
                }
            });
        }

        showCharCount() {
            var cc;
            try {
                $('#charcounts_text').show();
                $('#charcounts_raw').hide();
                cc = this.doc.getLength({noFootnotes: true, noThemes: true});
                $('#charcount').html(cc);
                $('#charcount_pages').html((Math.round(cc/18)/100).toLocaleString());

                cc = this.doc.getLength();
                $('#charcount_full').html(cc);
                $('#charcount_full_pages').html((Math.round(cc/18)/100).toLocaleString());
            }
            catch (e) {
                $('#charcounts_text').hide();
                $('#charcounts_raw').show();
                cc = this.doc.text.replace(/\s{2,}/g, ' ').length;
                $('#charcount_raw').html(cc);
                $('#charcount_raw_pages').html((Math.round(cc/18)/100).toLocaleString());
            }
        }

        onEnter(success, failure){
            super.onEnter();

            this.showCharCount();
        }
    }
    $.wiki.SummaryPerspective = SummaryPerspective;

})(jQuery);
