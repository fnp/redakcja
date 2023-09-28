(function($){

    let w = function() {};
    w = console.log;

    const elementDefs = {
        "ilustr": {
            "attributes": [
                {
                    "name": "src",
                    "type": "media",
                },
                {
                    "name": "alt",
                    "type": "text",
                },
                {
                    "name": "szer",
                    "type": "percent",
                },
                {
                    "name": "wyrownanie",
                    "type": "select",
                    "options": ["lewo", "srodek", "prawo"],
                },
                {
                    "name": "oblew",
                    "type": "bool",
                },
            ],
        },
        "ref": {
            "attributes": [
                {
                    "name": "href",
                },
            ],
        }
    };

    class PropertiesPerspective extends $.wiki.SidebarPerspective {
        vsplitbar = 'WŁAŚCIWOŚCI';
        $edited = null;

        constructor(options) {
            super(options);
                let self = this;

                self.$pane = $("#side-properties");

                $("#simple-editor").on('click', '[x-node]', function(e) {
                    if (!e.redakcja_edited) {
                        e.redakcja_edited = true;
                        self.edit(this);
                    }
                });

                self.$pane.on('click', '#parents li', function(e) {
                    self.edit($(this).data('node'));
                });

                $(document).on('click', '#bubbles .badge', function(e) {
                    self.edit($(this).data('node'));
                });

                self.$pane.on('change', '.form-control', function() {
                    let $input = $(this);

                    let inputval;
                    if ($input.attr('type') == 'checkbox') {
                        inputval = $input.is(':checked');
                    } else {
                        inputval = $input.val();
                    }

                    if ($input.data("edited")) {
                        if ($input.data("edited-attr")) {
                            $input.data("edited").attr($input.data("edited-attr"), inputval);
                        } else {
                            $input.data("edited").text(inputval);
                        }
                        $.wiki.perspectives.VisualPerspective.flush();
                        return;
                    }

                    html2text({
                        element: self.$edited[0],
                        success: function(xml) {
                            w(222)
                            let $xmlelem = $($.parseXML(xml));
                            w(333, $xmlelem)
                            w($input.data('property'), $input.val());
                            $xmlelem.contents().attr($input.data('property'), inputval);
                            w(444, $xmlelem)
                            let newxml = (new XMLSerializer()).serializeToString($xmlelem[0]);
                            w(555, newxml)
                            xml2html({
                                xml: newxml,
                                base: self.doc.getBase(),
                                success: function(html) {
                                    let htmlElem = $(html);
                                    self.$edited.replaceWith(htmlElem);
                                    self.edit(htmlElem);
                                    $.wiki.activePerspective().flush();
                                }
                            });
                        },
                        error: function(e) {console.log(e);},
                    });
                    self.$edited;
                });


                self.$pane.on('click', '.meta-add', function() {
                    // create a metadata item
                    let $fg = $(this).parent();
                    let ns = $fg.data('ns');
                    let tag = $fg.data('tag');
                    let field = $fg.data('field');
                    let span = $('<span/>');
                    span.attr('x-node', tag);
                    span.attr('x-ns', ns)
                    if (field.value_type.hasLanguage) {
                        span.attr('x-a-xml-lang', 'pl');
                    }

                    let rdf = $("> [x-node='RDF']", self.$edited);
                    if (!rdf.length) {
                        rdf = $("<span x-node='RDF' x-ns='http://www.w3.org/1999/02/22-rdf-syntax-ns#'>");
                        self.$edited.prepend(rdf);
                        self.$edited.prepend('\n  ');

                    }
                    let rdfdesc = $("> [x-node='Description']", rdf);
                    if (!rdfdesc.length) {
                        rdfdesc = $("<span x-node='Description' x-ns='http://www.w3.org/1999/02/22-rdf-syntax-ns#' x-a-rdf-about='" + self.doc.fullUri + "'>");
                        rdf.prepend(rdfdesc);
                        rdf.prepend('\n    ');
                        rdfdesc.append('\n    ');
                        rdf.append('\n  ');
                    }
                    span.appendTo(rdfdesc);
                    rdfdesc.append('\n    ');

                    self.displayMetaProperty($fg);

                    return false;
                });

                self.$pane.on('click', '.meta-delete', function() {
                    let $fg = $(this).closest('.form-group');
                    let $ig = $(this).closest('.input-group');
                    $('input', $ig).data('edited').remove();
                    self.displayMetaProperty($fg);
                    $.wiki.perspectives.VisualPerspective.flush();
                    return false;
                });

                $('#media-chooser').on('show.bs.modal', function (event) {
                    var input = $("input", $(event.relatedTarget).parent());
                    var modal = $(this);
                    modal.data('target-input', input);
                    var imglist = modal.find('.modal-body');
                    imglist.html('');
                    $.each(self.doc.galleryImages, (i, imgItem) => {
                        let img = $("<img>").attr("src", imgItem.thumb).attr('title', imgItem.url).data('url', imgItem.url).on('click', function() {
                            imglist.find('img').removeClass('active');
                            $(this).addClass('active');
                        });
                        imglist.append(img);
                    });
                })
                $('#media-chooser .ctrl-ok').on('click', function (event) {
                    $('#media-chooser').data('target-input')
                        .val(
                            (new URL($('#media-chooser .active').data('url'), document.baseURI)).href
                        ).trigger('change');
                    $('#media-chooser').modal('hide');
                });

            /* Meta chooser */
            $('#meta-chooser').on('show.bs.modal', function (event) {
                let input = $("input", $(event.relatedTarget).closest('.input-group'));
                let $fg = $(event.relatedTarget).closest('.form-group');
                let field = $fg.data('field');
                let modal = $(this);
                modal.data('target-input', input);
                let body = modal.find('.modal-body');
                body.html('');

                let add_options = function(cnt, options, value) {
                    $.each(options, (i, item) => {
                        let elem = $('<div class="form-check"><label class="form-check-label"><input class="form-check-input" type="radio" name="metachoose"><div class="value"></div><div class="name"></div><div class="description"></div></label></div>');
                        if (!item.usable) {
                            $('input', elem).remove();
                        }
                        if (item.hidden) {
                            $('input', elem).prop('disabled', 'disabled');
                        }
                        $('input', elem).val(item.value);
                        $('input', elem).val(item.value);
                        $('.value', elem).text(item.value);
                        $('.name', elem).append(item.name);
                        $('.description', elem).append(item.description);
                        let valueMatch = value && value.startsWith(item.value);
                        if (valueMatch) {
                            $('label', elem).addClass('text-primary')
                            if (value == item.value) {
                                $('input', elem).prop('checked', true);
                            }
                        }
                        if (item.sub) {
                            let subT = $('<div class="meta-chooser_toggle">+</div>');
                            let sub = $('<div>');
                            elem.append(subT);
                            elem.append(sub);
                            subT.on('click', () => {
                                sub.toggle()
                            });
                            add_options(sub, item.sub, valueMatch ? value : null);
                        }
                        elem.appendTo(cnt);
                    });
                };

                $.ajax({
                    url: field.value_type.chooser.source,
                    success: function(data) {
                        add_options(body, data, input.val());
                    }
                });
            })
            $('#meta-chooser .ctrl-ok').on('click', function (event) {
                $('#meta-chooser').data('target-input').val(
                    $('#meta-chooser :checked').val()
                ).trigger('change');
                $('#meta-chooser').modal('hide');
            });

                self.$pane.on('click', '.current-convert', function() {
                    self.convert($(this).attr('data-to'));
                });
                self.$pane.on('click', '#current-delete', function() {
                    self.delete();
                });
        }

        edit(element) {
            let self = this;

            $("#parents", self.$pane).empty();
            $("#bubbles").empty();

            let $f = $("#properties-form", self.$pane);
            $f.empty();

            if (element === null) {
                self.$edited = null;
                $("h1", self.$pane).text('');
                return;
            }

            let $node = $(element);
            let b = $("<div class='badge badge-primary'></div>").text($node.attr('x-node'));
            b.data('node', element);
            $("#bubbles").append(b);

            $node.parents('[x-node]').each(function() {
                let a = $("<li class='breadcrumb-item'>").text($(this).attr('x-node'));
                a.data('node', this);
                $("#parents", self.$pane).prepend(a)

                let b = $("<div class='badge badge-info'></div>").text($(this).attr('x-node'));
                b.data('node', this);
                $("#bubbles").append(b);
            })

            // It's a tag.
            let node = $(element).attr('x-node');
            $("h1", self.$pane).text(node);

            self.$edited = $(element);

            let nodeDef = elementDefs[node];
            if (nodeDef && nodeDef.attributes) {
                $.each(nodeDef.attributes, function(i, a) {
                    self.addEditField(a, $(element).attr('x-a-wl-' + a.name)); // ...
                })
            }

            // Only utwor can has matadata now.
            if (node == 'utwor') {
                $('<hr>').appendTo($("#properties-form", self.$pane))
                META_FIELDS.forEach(function(field) {
                    let $fg = $("<div class='form-group'>");
                    $("<label/>").text(field.name).appendTo($fg);

                    // if multiple?
                    $("<button class='meta-add float-right btn btn-primary'>+</button>").appendTo($fg);

                    let match = field.uri.match(/({(.*)})?(.*)/);
                    let ns = match[2];
                    let tag = match[3];

                    let cont = $('<div class="c">');

                    $fg.data('ns', ns);
                    $fg.data('tag', tag);
                    $fg.data('field', field);
                    cont.appendTo($fg);

                    self.displayMetaProperty($fg);

                    $fg.appendTo( $("#properties-form", self.$pane));
                });
            }

            // check node type, find relevant tags
            if ($node[0].nodeName == 'DIV') {
                $("#current-convert").attr("data-current-type", "div");
            } else if ($node[0].nodeName == 'EM') {
                $("#current-convert").attr("data-current-type", "span");
            }
        }

        addMetaInput(cont, field, element) {
            let self = this;

            let ig = $('<div class="input-group">');
            //ig.data('edited', element);
            ig.appendTo(cont);

            if (field.value_type.hasLanguage) {
                let pp = $("<div class='input-group-prepend'>");
                let lang_input = $("<input class='form-control' size='1' class='lang'>");
                lang_input.data('edited', $(element));
                lang_input.data('edited-attr', 'x-a-xml-lang');
                lang_input.val(
                    $(element).attr('x-a-xml-lang')
                );
                lang_input.appendTo(pp);
                pp.appendTo(ig);
            }

            let $aninput;
            if (field.value_type.widget == 'select') {
                $aninput = $("<select class='form-control'>");
                $.each(field.value_type.options, function() {
                    $("<option>").text(this).appendTo($aninput);
                })
            } else {
                $aninput = $("<input class='form-control'>");
                if (field.value_type.autocomplete) {
                    let autoOptions = field.value_type.autocomplete;
                    $aninput.autocomplete(autoOptions).autocomplete('instance')._renderItem = function(ul, item) {
                        let t = item.label;
                        if (item.name) t += '<br><small><strong>' + item.name + '</strong></small>';
                        if (item.description) t += '<br><small><em>' + item.description + '</em></small>';
                        return $( "<li>" )
                            .append( "<div>" + t + "</div>" )
                            .appendTo( ul );
                    };
                }
            }
            $aninput.data('edited', $(element))
            $aninput.val(
                $(element).text()
            );
            $aninput.appendTo(ig);

            let ap = $("<div class='input-group-append'>");
            ap.appendTo(ig);

            if (field.value_type.chooser) {
                ap.append($("<button type='button' class='btn btn-outline-secondary' data-toggle='modal' data-target='#meta-chooser'>…</button>"));
            }
            $("<button class='meta-delete btn btn-outline-secondary'>x</button>").appendTo(ap);

            // lang
        }

        displayMetaProperty($fg) {
            let self = this;
            let ns = $fg.data('ns');
            let tag = $fg.data('tag');
            let field = $fg.data('field');

            //  clear container
            $('.c', $fg).empty();

            let selector = "> [x-node='RDF'] > [x-node='Description'] > [x-node='"+tag+"']";
            if (ns) {
                selector += "[x-ns='"+ns+"']";
            }
            $(selector, self.$edited).each(function() {
                self.addMetaInput(
                    $('.c', $fg),
                    field,
                    this);
            });

            let count = $('.c > .input-group', $fg).length;
            if (field.required) {
                if (!count) {
                    $('<div class="text-warning">WYMAGANE</div>').appendTo($('.c', $fg));
                }
            }
        }

        addEditField(defn, value, elem) {
            let self = this;
            let $form = $("#properties-form", self.$pane);

            let $fg = $("<div class='form-group'>");
            $("<label/>").attr("for", "property-" + defn.name).text(defn.name).appendTo($fg);
            let $input, $inputCnt;
            switch (defn.type) {
            case 'text':
                $inputCnt =$input = $("<textarea>");
                break;
            case 'select':
                $inputCnt = $input = $("<select>");
                $.each(defn.options, function(i, e) {
                    $("<option>").text(e).appendTo($input);
                });
                break;
            case 'bool':
                $inputCnt = $input = $("<input type='checkbox'>");
                break;
            case 'media':
                $inputCnt = $("<div class='media-input input-group'>");
                $input = $("<input type='text'>");
                $inputCnt.append($input);
                $inputCnt.append($("<button type='button' class='ctrl-media-choose btn btn-primary' data-toggle='modal' data-target='#media-chooser'>…</button>"));
                break;
            default:
                $inputCnt = $input = $("<input>");
            }

            $input.addClass("form-control").attr("id", "property-" + defn.name).data("property", defn.name);
            if ($input.attr('type') == 'checkbox') {
                $input.prop('checked', value == 'true');
            } else {
                $input.val(value);
            }

            if (elem) {
                $input.data("edited", elem);
            }
            $inputCnt.appendTo($fg);

            $fg.appendTo($form);
        }

        convert(newtag) {
            this.$edited.attr('x-node', newtag);
            // TODO: take care of attributes?
        }

        delete(newtag) {
            p = this.$edited.parent();
            this.$edited.remove();
            this.edit(p);
        }

        onEnter(success, failure) {
            var self = this;
            super.onEnter();

            if ($.wiki.activePerspective() != 'VisualPerspective')
                $.wiki.switchToTab('#VisualPerspective');

            this.enable();
        }

        enable() {
            if (this.$edited === null) {
                this.edit($('[x-node="utwor"]')[0]);
            }
        }
        disable() {
            this.edit(null);
        }
    }
    $.wiki.PropertiesPerspective = PropertiesPerspective;

})(jQuery);
