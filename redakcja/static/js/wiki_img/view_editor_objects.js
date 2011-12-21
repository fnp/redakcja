(function($){

    function ObjectsPerspective(options){

        var old_callback = options.callback;

        options.callback = function(){
            var self = this;

            self.$tag_name = $('#objects-editor #tag-name');
            self.$objects_list = $('#objects-editor #objects-list');

            self.x1 = null;
            self.x2 = null;
            self.y1 = null;
            self.y2 = null;

            if (!CurrentDocument.readonly) {
                self.ias = $('#objects-editor img.area-selectable').imgAreaSelect({ handles: true, onSelectEnd: self._fillCoords(self), instance: true });
                $('#objects-editor #add').click(self._addObject(self));

                $('.delete', self.$objects_list).live('click', function() {
                    $(this).prev().trigger('click');
                    if (window.confirm("Czy na pewno chcesz usunąć ten obiekt?")) {
                        $(this).prev().remove();
                        $(this).remove();
                    }
                    self._resetSelection();
                    return false;
                });
            }

            $('.image-object', self.$objects_list).live('click', function(){
                $('.active', self.$objects_list).removeClass('active');
                $(this).addClass('active');
                var coords = $(this).data('coords');
                if (coords) {
                    self.ias.setSelection.apply(self.ias, coords);
                    self.ias.setOptions({ show: true });
                }
                else {
                    self._resetSelection();
                }
            });

            old_callback.call(this);
        };

        $.wiki.Perspective.call(this, options);
    };

    ObjectsPerspective.prototype = new $.wiki.Perspective();

    ObjectsPerspective.prototype.freezeState = function(){

    };

    ObjectsPerspective.prototype._resetSelection = function() {
        var self = this;
        self.x1 = self.x2 = self.y1 = self.y2 = null;
        self.ias.setOptions({ hide: true });
    }


    ObjectsPerspective.prototype._push = function(name, x1, y1, x2, y2) {
        var $e = $('<span class="image-object"></span>')
        $e.text(name);
        if (x1 !== null)
            $e.data('coords', [x1, y1, x2, y2]);
        this.$objects_list.append($e);
        this.$objects_list.append('<span class="delete">(x)</span>');
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

        $.each(this.doc.getImageItems('object'), function(i, e) {
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
            args.unshift($(e).text());
            objects.push(args);
        })
        self.doc.setImageItems('object', objects);

        this.ias.setOptions({disable: true, hide: true});

    };

    $.wiki.ObjectsPerspective = ObjectsPerspective;

})(jQuery);
