(function() { 
    jQuery.fn.getSelection = function() {
        var e = (this.jquery) ? this[0] : this;

        return (
            // Mozilla / dom 3.0
            ('selectionStart' in e && function() {
                var l = e.selectionEnd - e.selectionStart;
                return { start: e.selectionStart, end: e.selectionEnd, length: l, text: e.value.substr(e.selectionStart, l) };
            }) ||
            
            // Internet Explorer
            (document.selection && function() {
                e.focus();
                
                var r = document.selection.createRange();
                if (r === null) {
                    return { start: 0, end: e.value.length, length: 0 }
                }
                
                var re = e.createTextRange();
                var rc = re.duplicate();
                re.moveToBookmark(r.getBookmark());
                rc.setEndPoint('EndToStart', re);
                
                return { start: rc.text.length, end: rc.text.length + r.text.length, length: r.text.length, text: r.text };
            }) ||
            
            // browser not supported
            function() { return null; }
        )();
    },
        
    jQuery.fn.replaceSelection = function() {
        var e = this.jquery ? this[0] : this;
        var text = arguments[0] || '';
        var scrollTop = $(this).scrollTop();
                
        return (
            // Mozilla / dom 3.0
            ('selectionStart' in e && function() {
                var selectionStart = e.selectionStart;
                console.log(e.value.substr(0, e.selectionStart) + text + e.value.substr(e.selectionEnd, e.value.length));
                e.value = e.value.substr(0, e.selectionStart) + text + e.value.substr(e.selectionEnd, e.value.length);
                $(e).scrollTop(scrollTop).focus();
                e.selectionStart = selectionStart + text.length;
                e.selectionEnd = selectionStart + text.length;
                return this;
            }) ||

            // Internet Explorer
            (document.selection && function() {
                e.focus();
                document.selection.createRange().text = text;
                return this;
            }) ||

            // browser not supported
            function() {
                e.value += text;
                return jQuery(e);
            }
        )();
    }
})();