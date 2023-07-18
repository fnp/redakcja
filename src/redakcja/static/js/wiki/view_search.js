(function($){

    /*
     * Perspective
     */
    class SearchPerspective extends $.wiki.SidebarPerspective {
        constructor(options) {
            var old_callback = options.callback || function() { };

            options.callback = function(){
                var self = this;

                this.vsplitbar = 'ZNAJDŹ I ZAMIEŃ';
                this.editor = null;
                this.$element = $("#side-search");
                this.$searchInput = $('#search-input', this.$element);
                this.$replaceInput = $('#replace-input', this.$element);
                this.$searchButton = $('#search-button', this.$element);
                this.$searchPrevButton = $('#search-prev-button', this.$element);
                this.$replaceButton = $('#replace-button', this.$element);

                this.$replaceButton.attr("disabled","disabled");
                this.options = Array();

                // handlers
                this.$searchInput.change(function(event){
                    self.searchCursor = null;
                });
                this.$replaceInput.change(function(event){
                    self.searchCursor = null;
                });

                $("#side-search input:checkbox").each(function() {
                    self.options[this.id] = this.checked;
                }).change(function(){
                    self.options[this.id] = this.checked;
                    self.searchCursor = null;
                });

                this.$searchButton.click(function(){
                    if (!self.search())
                        alert('Brak wyników.');
                });

                this.$searchPrevButton.click(function(){
                    if (!self.search(false))
                        alert('Brak wyników.');
                });

                this.$replaceButton.click(function(){
                    self.replace();
                });

                old_callback.call(this);
            };

            super(options);
        }

        search(forward=true) {
            var self = this;
            var query = self.$searchInput.val();

            if (!self.editor)
                self.editor = $.wiki.perspectiveForTab('#CodeMirrorPerspective').codemirror

            if (!self.searchCursor) {
                var options = {};
                options.caseFold = !self.options['search-case-sensitive'];
                var start = 0;
                if (self.options['search-from-cursor']) {
                    start = self.editor.getCursor();
                }
                self.searchCursor = self.editor.getSearchCursor(
                    self.$searchInput.val(),
                    start,
                    options
                );
            }
            if (forward ? self.searchCursor.findNext() : self.searchCursor.findPrevious()) {
                self.editor.setSelection(self.searchCursor.from(), self.searchCursor.to());
                self.editor.scrollIntoView({from: self.searchCursor.from(), to: self.searchCursor.to()}, 20);
                self.$replaceButton.removeAttr("disabled");
                return true;
            }
            else {
                self.searchCursor = null;
                this.$replaceButton.attr("disabled","disabled");
                return false;
            }
        }

        replace() {
            var self = this;
            var query = self.$replaceInput.val();

            if (!self.searchCursor) {
                self.search();
            }
            else {}

            self.editor.setSelection(self.searchCursor.from(), self.searchCursor.to());
            self.editor.scrollIntoView({from: self.searchCursor.from(), to: self.searchCursor.to()}, 20);

            self.searchCursor.replace(query);
            if(self.search() && self.options['replace-all']) {
                self.replace();
            }
        }

        onEnter(success, failure) {
            var self = this;

            super.onEnter();
            self.$searchCursor = null;

            if ($.wiki.activePerspective() != 'CodeMirrorPerspective')
                $.wiki.switchToTab('#CodeMirrorPerspective');
        }

        onExit(success, failure) {
        }
    }

    $.wiki.SearchPerspective = SearchPerspective;

})(jQuery);
