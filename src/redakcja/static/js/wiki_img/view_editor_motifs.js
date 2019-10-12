(function($){

    function MotifsPerspective(options){
        var old_callback = options.callback;

        options.callback = function(){
            var self = this;
            this.$editor = $("#motifs-editor");
            this.object_type_name = "motyw";
            this.xml_object_type = 'theme';

            this._init();

            $.themes.autocomplete(self.$tag_name);

            old_callback.call(this);
        };

        $.wiki.Perspective.call(this, options);
    };

    MotifsPerspective.prototype = new $.wiki.ObjectsPerspective();

    $.wiki.MotifsPerspective = MotifsPerspective;

})(jQuery);
