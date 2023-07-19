(function($){

    /*
     * Perspective
     */
    class AnnotationsPerspective extends $.wiki.SidebarPerspective {
        vsplitbar = 'PRZYPISY';

        constructor(options) {
            super(options);

            var self = this;
            this.$element = $("#side-annotations");
            this.$error = $('.error-message', this.$element);
            this.$annos = $('.annotations-list', this.$element);
            this.$spinner = $('.spinner', this.$element);
            this.$refresh = $('.refresh', this.$element);

            this.$refresh.click(function() {
                var $this = $(this);

                self.$refresh.removeClass('active');
                $this.addClass('active');
                var atype = $this.attr('data-tag');

                self.$annos.hide();
                self.$error.hide();
                self.$spinner.fadeIn(100, function() {
                    self.refresh(atype);
                });
            });
        }

        updateAnnotationIds() {
            let selt = this;
            self.annotationToAnchor = {};
            $('#html-view').find('.annotation-inline-box').each(
                function(i, annoBox) {
                    var $annoBox = $(annoBox);
                    var $anchor = $("a[name|=anchor]", $annoBox);
                    var htmlContent = $('span', $annoBox).html();
                    // TBD: perhaps use a hash of htmlContent as key
                    self.annotationToAnchor[htmlContent] = $anchor.attr('name');
                }
            );
        }

        goToAnnotation(srcNode) {
            let self = this;
            var content = $(srcNode).html();
            content = content.replace(/&gt;/g, '>').replace(/&lt;/g, '<').replace(/&amp;/g, '&');
            xml2html({
                xml: '<root>'+content+'</root>',
                success: function(txt) {
                    content = $(txt).html();
                },
                error: function(text) {
                    $.unblockUI();
                    self.$error.html('<div class="alert alert-danger">' + text + '</div>');
                    self.$spinner.hide();
                    self.$error.show();
                }
            });

            var anchor = self.annotationToAnchor[content];
            if (anchor != undefined) {
                var $htmlView = $("#html-view");
                var top = $htmlView.offset().top +
                    $("[name=" + anchor + "]", $htmlView).offset().top -
                    $htmlView.children().eq(0).offset().top;

                $htmlView.animate({scrollTop: top}, 250);
            }
        }

        refresh(atype) {
            let self = this;
            var xml;

            var persp = $.wiki.activePerspective();
            if (persp == 'CodeMirrorPerspective') {
                xml = $.wiki.perspectives[persp].codemirror.getValue();
            }
            else if (persp == 'VisualPerspective') {
                html2text({
                    element: $('#html-view').find('div').get(0),
                    success: function(text){
                        xml = text;
                    },
                    error: function(text){
                        self.$error.html('<div class="alert alert-danger"><p>Wystąpił błąd:</p><pre>' + text + '</pre></div>');
                        self.$spinner.hide();
                        self.$error.show();
                    }
                });
                self.updateAnnotationIds();
            }
            else {
                xml = this.doc.text;
            }

            var parser = new DOMParser();
            var serializer = new XMLSerializer();
            var doc = parser.parseFromString(xml, 'text/xml');
            var error = $('parsererror', doc);

            if (error.length > 0) {
                self.$error.html('<div class="alert alert-danger">Błąd parsowania XML.</a>');
                self.$spinner.hide();
                self.$error.show();
            }
            else {
                self.$annos.html('');
                var anno_list = [];
                var annos = $(atype, doc);
                var counter = annos.length;
                var atype_rx = atype.replace(/,/g, '|');
                var ann_expr = new RegExp("^<("+atype_rx+")[^>]*>|</("+atype_rx+")>$", "g");

                if (annos.length == 0)
                {
                    self.$annos.html('<div class="alert alert-info">Nie ma żadnych przypisów</div>');
                    self.$spinner.hide();
                    self.$annos.show();
                }
                annos.each(function (i, elem) {
                    var xml_text = serializer.serializeToString(elem).replace(ann_expr, "");
                    xml2html({
                        xml: "<akap>" + xml_text + "</akap>",
                        success: function(xml_text){
                            return function(elem){
                                elem.sortby = $(elem).text().trim();
                                $(elem).append("<div class='src'>"+ xml_text.replace(/&/g, "&amp;").replace(/</g, "&lt;") +"</div>");
                                anno_list.push(elem);
                                $(".src", elem).click(function() { self.goToAnnotation(this); });
                                counter--;

                                if (!counter) {
                                    anno_list.sort(function(a, b){return a.sortby.localeCompare(b.sortby);});
                                    for (i in anno_list)
                                        self.$annos.append(anno_list[i]);
                                    self.$spinner.hide();
                                    self.$annos.show();
                                }
                            }
                        }(xml_text),
                        error: function(text) {
                            $.unblockUI();
                            self.$error.html('<div class="alert alert-danger">' + text + '</div>');
                            self.$spinner.hide();
                            self.$error.show();
                        }
                    });
                });
            }
        }

        onEnter() {
            super.onEnter();
            this.$refresh.filter('.active').trigger('click');
        };

        onExit(success, failure) {};
    }
    $.wiki.AnnotationsPerspective = AnnotationsPerspective;

})(jQuery);
