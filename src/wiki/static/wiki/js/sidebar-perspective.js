(function($) {

    
    SidebarPerspective = function(options) {
        this.noupdate_hash_onenter = true;
        $.wiki.Perspective.call(this, options);
    };
    
    SidebarPerspective.prototype = new $.wiki.Perspective();

    SidebarPerspective.prototype.onEnter = function(success, failure) {
        $.wiki.Perspective.prototype.onEnter.call(this);

        $('#vsplitbar').not('.active').trigger('click');
        $(".vsplitbar-title").text(this.vsplitbar);
    }
    
    $.wiki.SidebarPerspective = SidebarPerspective;


})(jQuery);
