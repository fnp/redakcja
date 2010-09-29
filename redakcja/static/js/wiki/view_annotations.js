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
            $('.refresh', this.$element).click(function() {
                self.refresh(self);
            });

			old_callback.call(this);
        };

        $.wiki.Perspective.call(this, options);
    };

    AnnotationsPerspective.prototype = new $.wiki.Perspective();

    AnnotationsPerspective.prototype.refresh = function(self) {
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
            self.$error.show();
            self.$annos.hide();
        }
        else {
            self.$error.hide();
            self.$annos.hide();
            self.$annos.html('');
            var anno_list = new Array();
            var annos = doc.getElementsByTagName('pe');
            var counter = annos.length;

            for (var i=0; i<annos.length; i++)
            {
                xml_text = serializer.serializeToString(annos[i]).replace(/^<pe[^>]*>|<\/pe>$/g, "");
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
                                self.$annos.show();
                            }
                        }
                    }(xml_text),
                    error: function(text) {
                        $.unblockUI();
                        self.$error.html(text);
                        self.$error.show();
                    }
                });
            }
        }
    }


    AnnotationsPerspective.prototype.onEnter = function(success, failure){
        var self = this;

        $.wiki.Perspective.prototype.onEnter.call(this);

        $('.vsplitbar').not('.active').trigger('click');
        $(".vsplitbar-title").html("&darr;&nbsp;PRZYPISY&nbsp;&darr;");

        this.refresh(this);

    };

	AnnotationsPerspective.prototype.onExit = function(success, failure) {

	};

    $.wiki.AnnotationsPerspective = AnnotationsPerspective;

})(jQuery);
