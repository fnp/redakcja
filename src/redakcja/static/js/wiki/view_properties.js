(function($){

    let w = function() {};
    w = console.log;
    
    const elementDefs = {
        "ilustr": {
            "attributes": [
                {
                    "name": "src",
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

    function PropertiesPerspective(options) {
        let oldCallback = options.callback || function() {};
        this.vsplitbar = 'WŁAŚCIWOŚCI';

        options.callback = function() {
            let self = this;

            self.$pane = $("#side-properties");
            
            $(document).on('click', '[x-node]', function(e) {
                if (!e.redakcja_edited) {
                    e.redakcja_edited = true;
                    self.edit(this);
                }
            });

            self.$pane.on('click', '#parents li', function(e) {
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
                    $input.data("edited").text(inputval);
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
                            }
                        });
                    },
                    error: function(e) {console.log(e);},
                });
                self.$edited;
            });
            
            oldCallback.call(this);
        };

        $.wiki.SidebarPerspective.call(this, options);
    }

    PropertiesPerspective.prototype = new $.wiki.SidebarPerspective();

    PropertiesPerspective.prototype.edit = function(element) {
        let self = this;

        let $node = $(element);
        $("#parents", self.$pane).empty();
        $node.parents('[x-node]').each(function() {
            let a = $("<li class='breadcrumb-item'>").text($(this).attr('x-node'));
            a.data('node', this);
            $("#parents", self.$pane).prepend(a)
        })
        // It's a tag.
        node = $(element).attr('x-node');
        $("h1", self.$pane).text(node);

        $f = $("#properties-form", self.$pane);
        $f.empty();
        self.$edited = $(element);

        let nodeDef = elementDefs[node];
        if (nodeDef && nodeDef.attributes) {
            $.each(nodeDef.attributes, function(i, a) {
                self.addEditField(a, $(element).attr('data-wlf-' + a.name)); // ...
            })
        }


        // Only utwor can has matadata now.
        if (node == 'utwor') {
            // Let's find all the metadata.
            $("> .RDF > .Description > [x-node]", $node).each(function() {
                $meta = $(this);
                self.addEditField(
                    {"name": $meta.attr('x-node'),},
                    $meta.text(),
                    $meta,
                );
            });
        }
    };
        
    PropertiesPerspective.prototype.addEditField = function(defn, value, elem) {
        let self = this;
        let $form = $("#properties-form", self.$pane);

        let $fg = $("<div class='form-group'>");
        $("<label/>").attr("for", "property-" + defn.name).text(defn.name).appendTo($fg);
        let $input;
        switch (defn.type) {
        case 'text':
            $input = $("<textarea>");
            break;
        case 'select':
            $input = $("<select>");
            $.each(defn.options, function(i, e) {
                $("<option>").text(e).appendTo($input);
            });
            break;
        case 'bool':
            $input = $("<input type='checkbox'>");
            break;
        default:
            $input = $("<input>");
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
        $input.appendTo($fg);

        $fg.appendTo($form);
    }
    
    $.wiki.PropertiesPerspective = PropertiesPerspective;

})(jQuery);

