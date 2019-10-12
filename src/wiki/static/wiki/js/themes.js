(function($) {

    $.themes = {};

    // Wykonuje block z załadowanymi kanonicznymi motywami
    $.themes.withCanon = function(code_block, onError) {
        if (typeof $.themes.canon == 'undefined') {
            $.ajax({
                url: '/editor/themes',
                dataType: 'text',
                success: function(data) {
                    $.themes.canon = data.split('\n');
                    code_block($.themes.canon);
                },
                error: function() {
                    $.themes.canon = null;
                    code_block($.themes.canon);
                }
            })
        }
        else {
            code_block($.themes.canon);
        }
    };

    function split( val ) {
        return val.split( /,\s*/ );
    }
    function extractLast( term ) {
        return split( term ).pop();
    }
 
    $.themes.autocomplete = function(elem) {
        elem.autocomplete({
            source: function(request, response) {
                var query = extractLast(request.term).toLowerCase();
                $.themes.withCanon(function(canonThemes) {
                    var candidates = [];
                    $.each(canonThemes, function(i, theme) {
                        if (theme.toLowerCase().startsWith(query)) {
                            candidates.push(theme);
                        }
                        if (candidates.length == 10) {
                            return false;
                        }
                    });
                    response(candidates);
                });
            },
            search: function() {
                var term = extractLast( this.value );
                if ( term.length < 1 ) {
                    return false;
                }
            },
            focus: function() {
                // prevent value inserted on focus
                return false;
            },
            select: function( event, ui ) {
                var terms = split( this.value );
                terms.pop();
                terms.push( ui.item.value );
                terms.push( "" );
                this.value = terms.join( ", " );
                return false;
            },
            appendTo: elem.parent()
        });
    };

    
})(jQuery);
