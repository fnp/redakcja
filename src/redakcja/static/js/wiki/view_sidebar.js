(function($) {

    class SidebarPerspective extends $.wiki.Perspective {
        noupdate_hash_onenter = true;

        onEnter(success, failure) {
            super.onEnter();

            $('#vsplitbar').not('.active').trigger('click');
            $(".vsplitbar-title").text(this.vsplitbar);
        }
    }
    $.wiki.SidebarPerspective = SidebarPerspective;

})(jQuery);
