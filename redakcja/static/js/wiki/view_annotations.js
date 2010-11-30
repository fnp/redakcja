(function($){

    /*
     * Perspective
     */
    function AnnotationsPerspective(options){
        var old_callback = options.callback || function() { };

        this.noupdate_hash_onenter = true;
        this.vsplitbar = 'PRZYPISY';

        options.callback = function(){
            var self = this;

            this.$element = $("#side-annotations");
            this.$error = $('.error-message', this.$element);
            this.$annos = $('.annotations-list', this.$element);
            this.$spinner = $('.spinner', this.$element);
            this.$refresh = $('.refresh', this.$element);

            this.$refresh.click(function() {
                $this = $(this);

                self.$refresh.removeClass('active');
                $this.addClass('active');
                atype = $this.attr('data-tag');

                self.$annos.hide();
                self.$error.hide();
                self.$spinner.show(100, function(){
                    self.refresh(self, atype);
                });
            });

			old_callback.call(this);
        };

        $.wiki.Perspective.call(this, options);
    };

    AnnotationsPerspective.prototype = new $.wiki.Perspective();

    AnnotationsPerspective.prototype.refresh = function(self, atype) {
        var xml;

        persp = $.wiki.activePerspective();
        if (persp == 'CodeMirrorPerspective') {
            xml = $.wiki.perspectives[persp].codemirror.getCode();
        }
        else if (persp == 'VisualPerspective') {
            html2text({
                element: $('#html-view div').get(0),
                success: function(text){
                    xml = text;
                },
                error: function(text){
                    self.$error.html('<p>Wystąpił błąd:</p><pre>' + text + '</pre>');
                    self.$spinner.hide();
                    self.$error.show();
                }
            });
        }
        else {
            xml = this.doc.text;
        }

        var parser = new DOMParser();
        var serializer = new XMLSerializer();
        var doc = parser.parseFromString(xml, 'text/xml');
        var error = $('parsererror', doc);

        if (error.length > 0) {
            self.$error.html('Błąd parsowania XML.');
            self.$spinner.hide();
            self.$error.show();
        }
        else {
            self.$annos.html('');
            var anno_list = new Array();
            var annos = $(atype, doc);
            var counter = annos.length;
            var atype_rx = atype.replace(/,/g, '|');
            var ann_expr = new RegExp("^<("+atype_rx+")[^>]*>|</("+atype_rx+")>$", "g")

            if (annos.length == 0)
            {
                self.$annos.html('Nie ma żadnych przypisów');
                self.$spinner.hide();
                self.$annos.show();
            }
            annos.each(function (i, elem) {
                xml_text = serializer.serializeToString(elem).replace(ann_expr, "");
                xml2html({
                    xml: "<akap>" + xml_text + "</akap>",
                    success: function(xml_text){
                        return function(elem){
                            elem.sortby = $(elem).text().trim();
                            $(elem).append("<div class='src'>"+ xml_text.replace("&", "&amp;", "g").replace("<", "&lt;", "g") +"</div>")
                            anno_list.push(elem);
                            counter--;

                            if (!counter) {
                                anno_list.sort(function(a, b){return a.sortby.localeCompare(b.sortby);});
                                self.$annos.append(anno_list);
                                self.$spinner.hide();
                                self.$annos.show();
                            }

                        }
                    }(xml_text),
                    error: function(text) {
                        $.unblockUI();
                        self.$error.html(text);
                        self.$spinner.hide();
                        self.$error.show();
                    }
                });
            });
        }
    }


    AnnotationsPerspective.prototype.onEnter = function(success, failure){
        var self = this;

        $.wiki.Perspective.prototype.onEnter.call(this);

        $('.vsplitbar').not('.active').trigger('click');
        $(".vsplitbar-title").html("&darr;&nbsp;PRZYPISY&nbsp;&darr;");
        this.$refresh.filter('.active').trigger('click');

    };

	AnnotationsPerspective.prototype.onExit = function(success, failure) {

	};

    $.wiki.AnnotationsPerspective = AnnotationsPerspective;

})(jQuery);
