(function($){

    function ObjectsPerspective(options){
        if (!options) return;

        var old_callback = options.callback;

        options.callback = function(){
            this.$editor = $("#objects-editor");
            this.object_type_name = "obiekt";
            this.xml_object_type = 'object';
            this._init();
            old_callback.call(this);
        };

        $.wiki.Perspective.call(this, options);
    };

    ObjectsPerspective.prototype = new $.wiki.Perspective();

    ObjectsPerspective.prototype._init = function() {
            var self = this;

            self.$tag_name = $('.tag-name', self.$editor);
            self.$toolbar = $('.toolbar', self.$editor);
            self.$scrolled = $('.scrolled', self.$editor);
            self.$objects_list = $('.objects-list', self.$editor);

            self.x1 = null;
            self.x2 = null;
            self.y1 = null;
            self.y2 = null;

            if (!CurrentDocument.readonly) {
                self.ias = $('img.area-selectable', self.$editor).imgAreaSelect({
                    handles: true,
                    instance: true,
                    onSelectEnd: self._fillCoords(self),
                    onSelectChange: function() {self._cropSelection();},
                });
                $('.add', self.$editor).click(self._addObject(self));

                $(self.$objects_list).on('click', '.delete', function() {
                    $(this).parent().trigger('click');
                    if (window.confirm("Czy na pewno chcesz usunąć ten " + object_type_name + "?")) {
                        $(this).parent().remove();
                    }
                    self._resetSelection();
                    return false;
                });
            }

            $(self.$objects_list).on('click', '.image-object', function(){
                $('.active', self.$objects_list).removeClass('active');
                $(this).addClass('active');
                var coords = $(this).data('coords');
                if (coords) {
                    self.ias.setSelection.apply(self.ias, coords);
                    self.ias.setOptions({ show: true });
                    self._cropSelection();
                }
                else {
                    self._resetSelection();
                }
            });

            self.$scrolled.scroll(function() {
                self.ias.update();
                self._cropSelection();
            });
    }

    ObjectsPerspective.prototype._cropSelection = function() {
        var mintop = this.$scrolled.offset().top;
        var maxbottom = mintop + this.$scrolled.height();
        $(".imgareaselect-outer").each(function(i, e) {
            var top = parseInt(e.style.top);
            var height = parseInt(e.style.height);
            var bottom = top + height;
            dtop = dheight = 0;
            if (top < mintop) {
                dtop += mintop - top;
                dheight -= dtop;
            }
            if (bottom > maxbottom) {
                dheight -= bottom - maxbottom;
            }
            if (dtop) {
                e.style.top = top + dtop + 'px';
            }
            if (dheight) {
                e.style.height = Math.max(0, height + dheight) + 'px';
            }
        });
    }

    ObjectsPerspective.prototype._resetSelection = function() {
        var self = this;
        self.x1 = self.x2 = self.y1 = self.y2 = null;
        self.ias.setOptions({ hide: true });
    }

    ObjectsPerspective.prototype._push = function(name, x1, y1, x2, y2) {
        var $e = $('<span class="image-object btn btn-outline-light mr-1"><span class="name"></span><span class="delete badge badge-danger ml-2">x</span></span>');
        $(".name", $e).text(name);
        if (x1 !== null)
            $e.data('coords', [x1, y1, x2, y2]);
        this.$objects_list.append($e);
    }


    ObjectsPerspective.prototype._addObject = function(self) {
        return function() {
            outputs = [];
            chunks = self.$tag_name.val().split(',');
            for (i in chunks) {
                item = chunks[i].trim();
                if (item == '')
                    continue;
                outputs.push(item.trim());
            }
            output = outputs.join(', ');

            self._push(output, self.x1, self.y1, self.x2, self.y2);
            self._resetSelection();
        }
    }

    ObjectsPerspective.prototype._fillCoords = function(self) {
        return function(img, selection) {
            $('.active', self.$objects_list).removeClass('active');
            if (selection.x1 != selection.x2 && selection.y1 != selection.y2) {
                self.x1 = selection.x1;
                self.x2 = selection.x2;
                self.y1 = selection.y1;
                self.y2 = selection.y2;
            }
            else {
                self.x1 = self.x2 = self.y1 = self.y2 = null;
            }
        }
    }

    ObjectsPerspective.prototype.onEnter = function(success, failure){
        var self = this;
        this.$objects_list.children().remove();

        $.each(this.doc.getImageItems(self.xml_object_type), function(i, e) {
            self._push.apply(self, e);
        });

        if (this.x1 !== null)
            this.ias.setOptions({enable: true, show: true});
        else
            this.ias.setOptions({enable: true});

        $.wiki.Perspective.prototype.onEnter.call(this);

    };

    ObjectsPerspective.prototype.onExit = function(success, failure){
        var self = this;
        var objects = [];
        this.$objects_list.children(".image-object").each(function(i, e) {
            var args = $(e).data('coords');
            if (!args)
                args = [null, null, null, null];
            args.unshift($(".name", e).text());
            objects.push(args);
        })
        self.doc.setImageItems(self.xml_object_type, objects);

        this.ias.setOptions({disable: true, hide: true});

    };

    $.wiki.ObjectsPerspective = ObjectsPerspective;

})(jQuery);
