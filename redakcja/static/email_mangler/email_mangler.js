var rot13 = function(s){
    return s.replace(/[a-zA-Z]/g, function(c){
        return String.fromCharCode((c <= "Z" ? 90 : 122) >= (c = c.charCodeAt(0) + 13) ? c : c - 26);
    });
};

(function($) {
    $(function() {

        $(".mangled").each(function() {
            $this = $(this);
            var email = rot13($this.attr('data-addr1')) + '@' +
                rot13($this.attr('data-addr2'));
            $this.attr('href', "mailto:" + email);
            $this.html(email);
        });


    });
})(jQuery);

