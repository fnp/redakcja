(function($) {

    /* Show theme to the user */
    function selectTheme(themeId){
        var selection = window.getSelection();
        selection.removeAllRanges();

        var range = document.createRange();
        var s = $("[x-node='motyw'][theme-class='" + themeId + "']")[0];
        var e = $("[x-node='end'][theme-class='" + themeId + "']")[0];

        if (s && e) {
            range.setStartAfter(s);
            range.setEndBefore(e);
            selection.addRange(range);
        }
    };

    /* Verify insertion port for annotation or theme */
    function verifyTagInsertPoint(node){
        if (node.nodeType == Node.TEXT_NODE) {
            node = node.parentNode;
        }

        if (node.nodeType != Node.ELEMENT_NODE) {
            return false;
        }

        node = $(node);
        if (node.attr('id') == 'caret') {
            node = node.parent();
        }
        while (node.attr('x-pass-thru')) {
            node = node.parent();
        }
        var xtype = node.attr('x-node');

        if (!xtype || (xtype.search(':') >= 0) ||
        xtype == 'motyw' ||
        xtype == 'begin' ||
        xtype == 'end') {
            return false;
        }

        return true;
    }

    function verifyThemeBoundaryPoint(node) {
        if (!verifyTagInsertPoint(node)) return false;
        node = $(node);
        // don't allow themes inside annotations
        if (node.closest('[x-node="pe"]').length > 0)
            return false;

        return true;
    }

    /* Convert HTML fragment to plaintext */
    var ANNOT_FORBIDDEN = ['pt', 'pa', 'pr', 'pe', 'ptrad', 'begin', 'end', 'motyw'];

    function html2plainText(fragment){
        var text = "";

        $(fragment.childNodes).each(function(){
            if (this.nodeType == Node.TEXT_NODE)
                text += this.nodeValue;
            else {
                if (this.nodeType == Node.ELEMENT_NODE &&
                        $.inArray($(this).attr('x-node'), ANNOT_FORBIDDEN) == -1) {
                    text += html2plainText(this);
                }
            };
        });

        return text;
    }


    /* Insert annotation using current selection */
    function addAnnotation(){
        var selection = window.getSelection();
        var n = selection.rangeCount;

        if (selection.isCollapsed) {
            window.alert("Nie zaznaczono żadnego obszaru");
            return false;
        }

        var range = selection.getRangeAt(n - 1);

        if (!verifyTagInsertPoint(range.endContainer)) {
            window.alert("Nie można wstawić w to miejsce przypisu.");
            return false;
        }

        text = '';
        for (let i = 0; i < n; ++ i) {
            let rangeI = selection.getRangeAt(i);
            if (verifyTagInsertPoint(rangeI.startContainer) &&
                verifyTagInsertPoint(rangeI.endContainer)) {
                text += html2plainText(rangeI.cloneContents());
            }
        }
        var tag = $('<span></span>');
        range.collapse(false);
        range.insertNode(tag[0]);

        xml2html({
            xml: '<pe><slowo_obce>' + text + '</slowo_obce> --- </pe>',
            success: function(text){
                var t = $(text);
                tag.replaceWith(t);
                openForEdit(t, trim=false);
            },
            error: function(){
                tag.remove();
                alert('Błąd przy dodawaniu przypisu:' + errors);
            }
        })
    }



    /* Insert theme using current selection */

    function addTheme(){
        var selection = window.getSelection();
        var n = selection.rangeCount;

        if (n == 0) {
            window.alert("Nie zaznaczono żadnego obszaru");
            return false;
        }

        // for now allow only 1 range
        if (n > 1) {
            window.alert("Zaznacz jeden obszar.");
            return false;
        }

        // remember the selected range
        var range = selection.getRangeAt(0);

        if ($(range.startContainer).is('.html-editarea') ||
        $(range.endContainer).is('.html-editarea')) {
            window.alert("Motywy można oznaczać tylko na tekście nie otwartym do edycji. \n Zamknij edytowany fragment i spróbuj ponownie.");
            return false;
        }

        // verify if the start/end points make even sense -
        // they must be inside a x-node (otherwise they will be discarded)
        // and the x-node must be a main text
        if (!verifyThemeBoundaryPoint(range.startContainer)) {
            window.alert("Motyw nie może się zaczynać w tym miejscu.");
            return false;
        }

        if (!verifyThemeBoundaryPoint(range.endContainer)) {
            window.alert("Motyw nie może się kończyć w tym miejscu.");
            return false;
        }

        var date = (new Date()).getTime();
        var random = Math.floor(4000000000 * Math.random());
        var id = ('' + date) + '-' + ('' + random);

        var createPoint = function(container, offset) {
            var offsetBetweenCommas = function(text, offset) {
                if(text.length < 2 || offset < 1 || offset > text.length)
                    return false;
                return text[offset-1] === ',' && text[offset] === ',';
            }
            var point = document.createRange();
            offset = offsetBetweenCommas(container.textContent, offset) ? offset - 1 : offset;
            point.setStart(container, offset);
            return point;
        }

        var spoint = createPoint(range.startContainer, range.startOffset);
        var epoint = createPoint(range.endContainer, range.endOffset);

        var mtag, btag, etag, errors;

        // insert theme-ref

        xml2html({
            xml: '<end id="e' + id + '" />',
            success: function(text){
                etag = $('<span></span>');
                epoint.insertNode(etag[0]);
                etag.replaceWith(text);
                xml2html({
                    xml: '<motyw id="m' + id + '"></motyw>',
                    success: function(text){
                        mtag = $('<span></span>');
                        spoint.insertNode(mtag[0]);
                        mtag.replaceWith(text);
                        xml2html({
                            xml: '<begin id="b' + id + '" />',
                            success: function(text){
                                btag = $('<span></span>');
                                spoint.insertNode(btag[0])
                                btag.replaceWith(text);
                                selection.removeAllRanges();
                                openForEdit($('[x-node="motyw"][theme-class="' + id + '"]'));
                            }
                        });
                    }
                });
            }
        });
    }

    function addSymbol(caret) {
        let editArea;

        if (caret) {
            editArea = $("textarea", caret.element)[0];
        } else {
            editArea = $('div.html-editarea textarea')[0];
        }

        if(editArea) {
            var specialCharsContainer = $("<div id='specialCharsContainer'><a href='#' id='specialCharsClose'>Zamknij</a><table id='tableSpecialChars' style='width: 600px;'></table></div>");

            var specialChars = [
                ' ', 'Ą','ą','Ć','ć','Ę','ę','Ł','ł','Ń','ń','Ó','ó','Ś','ś','Ż','ż','Ź','ź','Á','á','À','à',
                'Â','â','Ä','ä','Å','å','Ā','ā','Ă','ă','Ã','ã',
                'Æ','æ','Ç','ç','Č','č','Ċ','ċ','Ď','ď','É','é','È','è',
                'Ê','ê','Ë','ë','Ē','ē','Ě','ě','Ġ','ġ','Ħ','ħ','Í','í','Î','î',
                'Ī','ī','Ĭ','ĭ','Ľ','ľ','Ñ','ñ','Ň','ň','Ó','ó','Ö','ö',
                'Ô','ô','Ō','ō','Ǒ','ǒ','Œ','œ','Ø','ø','Ř','ř','Š',
                'š','Ş','ş','Ť','ť','Ţ','ţ','Ű','ű','Ú','ú','Ù','ù',
                'Ü','ü','Ů','ů','Ū','ū','Û','û','Ŭ','ŭ',
                'Ý','ý','Ž','ž','ß','Ð','ð','Þ','þ','А','а','Б',
                'б','В','в','Г','г','Д','д','Е','е','Ё','ё','Ж',
                'ж','З','з','И','и','Й','й','К','к','Л','л','М',
                'м','Н','н','О','о','П','п','Р','р','С','с',
                'Т','т','У','у','Ф','ф','Х','х','Ц','ц','Ч',
                'ч','Ш','ш','Щ','щ','Ъ','ъ','Ы','ы','Ь','ь','Э',
                'э','Ю','ю','Я','я','ѓ','є','і','ї','ј','љ','њ',
                'Ґ','ґ','Α','α','Β','β','Γ','γ','Δ','δ','Ε','ε',
                'Ζ','ζ','Η','η','Θ','θ','Ι','ι','Κ','κ','Λ','λ','Μ',
                'μ','Ν','ν','Ξ','ξ','Ο','ο','Π','π','Ρ','ρ','Σ','ς','σ',
                'Τ','τ','Υ','υ','Φ','φ','Χ','χ','Ψ','ψ','Ω','ω','–',
                '—','¡','¿','$','¢','£','€','©','®','°','¹','²','³',
                '¼','½','¾','†','§','‰','•','←','↑','→','↓',
                '„','”','„”','«','»','«»','»«','’','[',']','~','|','−','·',
                '×','÷','≈','≠','±','≤','≥','∈',

                // Hebrew
                '\u05d0', '\u05d1', '\u05d2', '\u05d3', '\u05d4', '\u05d5', '\u05d6', '\u05d7',
                '\u05d8', '\u05d9', '\u05da', '\u05db', '\u05dc', '\u05dd', '\u05de', '\u05df', 
                '\u05e0', '\u05e1', '\u05e2', '\u05e3', '\u05e4', '\u05e5', '\u05e6', '\u05e7', 
                '\u05e8', '\u05e9', '\u05e0', '\u05ea',

                '\u0591', '\u0592', '\u0593', '\u0594', '\u0595', '\u0596', '\u0597',
                '\u0598', '\u0599', '\u059a', '\u059b', '\u059c', '\u059d', '\u059e', '\u059f', 
                '\u05a0', '\u05a1', '\u05a2', '\u05a3', '\u05a4', '\u05a5', '\u05a6', '\u05a7',
                '\u05a8', '\u05a9', '\u05aa', '\u05ab', '\u05ac', '\u05ad', '\u05ae', '\u05af', 
                '\u05b0', '\u05b1', '\u05b2', '\u05b3', '\u05b4', '\u05b5', '\u05b6', '\u05b7',
                '\u05b8', '\u05b9', '\u05ba', '\u05bb', '\u05bc', '\u05bd', '\u05be', '\u05bf', 
                '\u05c0', '\u05c1', '\u05c2', '\u05c3', '\u05c4', '\u05c5', '\u05c6', '\u05c7',

                '\ufb1d', '\ufb1e', '\ufb1f',
                '\ufb20', '\ufb21', '\ufb22', '\ufb23', '\ufb24', '\ufb25', '\ufb26', '\ufb27',
                '\ufb28', '\ufb29', '\ufb2a', '\ufb2b', '\ufb2c', '\ufb2d', '\ufb2e', '\ufb2f',
                '\ufb30', '\ufb31', '\ufb32', '\ufb33', '\ufb34', '\ufb35', '\ufb36',
                '\ufb38', '\ufb39', '\ufb3a', '\ufb3b', '\ufb3c',           '\ufb3e',
                '\ufb40', '\ufb41',           '\ufb43', '\ufb44',           '\ufb46', '\ufb47',
                '\ufb48', '\ufb49', '\ufb4a', '\ufb4b', '\ufb4c', '\ufb4d', '\ufb4e', '\ufb4f', 
            ]
            var tableContent = "<tr>";

            for(var i in specialChars) {
                if(i % 14 == 0 && i > 0) {
                    tableContent += "</tr><tr>";
                }
                tableContent += "<td><input type='button' class='specialBtn' value='"+specialChars[i]+"'/></td>";
            }

            tableContent += "</tr>";
            $("body").append(specialCharsContainer);


             // localStorage for recently used characters - reading
             if (typeof(localStorage) != 'undefined') {
                 if (localStorage.getItem("recentSymbols")) {
                     var recent = localStorage.getItem("recentSymbols");
                     var recentArray = recent.split(";");
                     var recentRow = "";
                     for(var i in recentArray.reverse()) {
                        recentRow += "<td><input type='button' class='specialBtn recentSymbol' value='"+recentArray[i]+"'/></td>";
                     }
                     recentRow = "<tr>" + recentRow + "</tr>";
                 }
             }
            $("#tableSpecialChars").append(recentRow);
            $("#tableSpecialChars").append(tableContent);

            /* events */

            $('.specialBtn').click(function(){
                var insertVal = $(this).val();

                // if we want to surround text with quotes
                // not sure if just check if value has length == 2

                if (caret) {
                    caret.insertChar(insertVal);
                    caret.focus();
                } else {
                    if (insertVal.length == 2) {
                        var startTag = insertVal[0];
                        var endTag = insertVal[1];
                        var textAreaOpened = editArea;
                        //IE support
                        if (document.selection) {
                            textAreaOpened.focus();
                            sel = document.selection.createRange();
                            sel.text = startTag + sel.text + endTag;
                        }
                        //MOZILLA/NETSCAPE support
                        else if (textAreaOpened.selectionStart || textAreaOpened.selectionStart == '0') {
                            var startPos = textAreaOpened.selectionStart;
                            var endPos = textAreaOpened.selectionEnd;
                            textAreaOpened.value = textAreaOpened.value.substring(0, startPos)
                                + startTag + textAreaOpened.value.substring(startPos, endPos) + endTag + textAreaOpened.value.substring(endPos, textAreaOpened.value.length);
                        }
                    } else {
                        insertAtCaret(editArea, insertVal);
                    }
                }

                // localStorage for recently used characters - saving
                if (typeof(localStorage) != 'undefined') {
                    if (localStorage.getItem("recentSymbols")) {
                        var recent = localStorage.getItem("recentSymbols");
                        var recentArray = recent.split(";");
                        var valIndex = $.inArray(insertVal, recentArray);
                        //alert(valIndex);
                        if(valIndex == -1) {
                            // value not present in array yet
                            if(recentArray.length > 13){
                                recentArray.shift();
                                recentArray.push(insertVal);
                            } else {
                                recentArray.push(insertVal);
                            }
                        } else  {
                            // value already in the array
                            for(var i = valIndex; i < recentArray.length; i++){
                                recentArray[i] = recentArray[i+1];
                            }
                            recentArray[recentArray.length-1] = insertVal;
                        }
                        localStorage.setItem("recentSymbols", recentArray.join(";"));
                    } else {
                        localStorage.setItem("recentSymbols", insertVal);
                    }
                }
                $(specialCharsContainer).remove();
            });
            $('#specialCharsClose').click(function(){
                $(specialCharsContainer).remove();
            });

        } else {
            window.alert('Najedź na fragment tekstu, wybierz "Edytuj" i ustaw kursor na miejscu gdzie chcesz wstawić symbol.');
        }
    }

    function insertAtCaret(txtarea,text) {
        /* http://www.scottklarr.com/topic/425/how-to-insert-text-into-a-textarea-where-the-cursor-is/ */
        var scrollPos = txtarea.scrollTop;
        var strPos = 0;
        var backStart = 0;
        var br = ((txtarea.selectionStart || txtarea.selectionStart == '0') ? "ff" : (document.selection ? "ie" : false ) );
        if (br == "ie") {
            txtarea.focus();
            var range = document.selection.createRange();
            range.moveStart ('character', -txtarea.value.length);
            strPos = backStart = range.text.length;
        } else if (br == "ff") {
            strPos = txtarea.selectionStart;
            backStart = txtarea.selectionEnd;
        }
        var front = (txtarea.value).substring(0,strPos);
        var back = (txtarea.value).substring(backStart,txtarea.value.length);
        txtarea.value=front+text+back;
        strPos = strPos + text.length;
        if (br == "ie") {
            txtarea.focus();
            var range = document.selection.createRange();
            range.moveStart ('character', -txtarea.value.length);
            range.moveStart ('character', strPos);
            range.moveEnd ('character', 0);
            range.select();
        } else if (br == "ff") {
            txtarea.selectionStart = strPos;
            txtarea.selectionEnd = strPos;
            txtarea.focus();
        }
        txtarea.scrollTop = scrollPos;
    }

    /* open edition window for selected fragment */
    function openForEdit($origin, trim=true){
        var $box = null

        // annotations overlay their sub box - not their own box //
        if ($origin.is(".annotation-inline-box")) {
            $box = $("*[x-annotation-box]", $origin);
        }
        else {
            $box = $origin;
        }
        var x = $box[0].offsetLeft;
        var y = $box[0].offsetTop;

        var w = $box.outerWidth();
        var h = $box.innerHeight();

        if ($origin.is(".annotation-inline-box")) {
            w = Math.max(w, 400);
            h = Math.max(h, 60);
            if($('.htmlview div').offset().left + $('.htmlview div').width() > ($('.vsplitbar').offset().left - 480)){
                x = -(Math.max($origin.offset().left, $origin.width()));
            } else {
                x = 100;
            }
        }
        if ($origin.is('.reference-inline-box')) {
            w = 400;
            h = 32;
            y -= 32;
            x = Math.min(
                x,
                $('.htmlview div').offset().left + $('.htmlview div').width() - 400
            );
        }

        // start edition on this node
        var $overlay = $('<div class="html-editarea"><div class="html-editarea-toolbar"><div class="html-editarea-toolbar-left"><button class="accept-button">Zapisz</button><button class="delete-button">Usuń</button></div><div class="html-editarea-toolbar-right"><button class="akap-edit-button" data-tag="tytul_dziela">tytuł dzieła</button><button class="akap-edit-button" data-tag="wyroznienie">wyróżnienie</button><button class="akap-edit-button" data-tag="slowo_obce">słowo obce</button><button class="akap-edit-button" data-tag-selfclosing="br">br</button><button class="akap-edit-button" data-act="spec">znak spec.</button></div></div><textarea></textarea></div>').css({
            position: 'absolute',
            height: h,
            left: x,
            top: y,
            width: w
        }).appendTo($box[0].offsetParent || $box.parent()).show();


        if ($origin.is('*[x-edit-no-format]')) {
            $('.akap-edit-button').remove();
        }

        if ($origin.is('[x-node="motyw"]')) {
            $.themes.autocomplete($('textarea', $overlay));
        }

        if ($origin.is('[x-node="motyw"]')){
            $('.delete-button', $overlay).click(function(){
                if (window.confirm("Czy jesteś pewien, że chcesz usunąć ten motyw?")) {
                    $('[theme-class="' + $origin.attr('theme-class') + '"]').remove();
                    $overlay.remove();
                    $(document).unbind('click.blur-overlay');
                    return false;
                };
            });
        }
        else if($box.is('*[x-annotation-box]') || $origin.is('*[x-edit-attribute]') || $origin.is('*[x-node="uwaga"]')) {
            let q;
            switch ($origin.attr('x-node')) {
            case 'uwaga':
                q = 'tę uwagę';
                break;
            case 'ref':
                q = 'tę referencję';
                break
            default:
                q = 'ten przypis';
            }
            $('.delete-button', $overlay).click(function(){
                if (window.confirm("Czy jesteś pewien, że chcesz usunąć " + q + "?")) {
                    $origin.remove();
                    $overlay.remove();
                    $(document).unbind('click.blur-overlay');
                    return false;
                };
            });
        }
        else {
            $('.delete-button', $overlay).html("Anuluj");
            $('.delete-button', $overlay).click(function(){
                if (window.confirm("Czy jesteś pewien, że chcesz anulować zmiany?")) {
                    $overlay.remove();
                    $(document).unbind('click.blur-overlay');
                    return false;
                };
            });
        }


        var serializer = new XMLSerializer();

        if($box.attr("x-edit-attribute")) {
            source = $('<span x-pass-thru="true"/>');
            source.text($box.attr("x-a-wl-" + $box.attr("x-edit-attribute")));
            source = source[0];
        } else {
            source = $box[0];
        }

        html2text({
            element: source,
            stripOuter: true,
            success: function(text){
		let ttext = text;
		if (trim) {
		    ttext = ttext.trim();
		}
                $('textarea', $overlay).val(ttext);

                setTimeout(function(){
                    $('textarea', $overlay).elastic().focus();
                }, 50);

                function save(argument){
                    var nodeName = $box.attr('x-node') || 'pe';
                    var insertedText = $('textarea', $overlay).val();

                    if ($origin.is('[x-node="motyw"]')) {
                        insertedText = insertedText.replace(/,\s*$/, '');
                    }

                    if($box.attr("x-edit-attribute")) {
                        xml = '<' + nodeName + ' ' + $box.attr("x-edit-attribute") + '="' + insertedText + '"/>';
                    } else {
                        xml = '<' + nodeName + '>' + insertedText + '</' + nodeName + '>';
                    }

                    xml2html({
                        xml: xml,
                        success: function(element){
                            if (nodeName == 'out-of-flow-text') {
                                $(element).children().insertAfter($origin);
                                $origin.remove()
                            }
                            else if ($box.attr('x-edit-attribute')) {
                                $(element).insertAfter($origin);
                                $origin.remove();
                            }
                            else {
                                $origin.html($(element).html());
                            }
                            $overlay.remove();
                            $.wiki.activePerspective().flush();
                        },
                        error: function(text){
                            alert('Błąd! ' + text);
                        }
                    })

                    var msg = $("<div class='saveNotify'><p>Pamiętaj, żeby zapisać swoje zmiany.</p></div>");
                    $("#base").prepend(msg);
                    $('#base .saveNotify').fadeOut(3000, function(){
                        $(this).remove();
                    });
                }

                $('.akap-edit-button', $overlay).click(function(){
                    var textAreaOpened = $('textarea', $overlay)[0];
                    var startTag = "";
                    var endTag = "";
                    var tag = "";
                    var $this = $(this);

                    if ($this.data('tag')) {
                        tag = $this.data('tag');
                        startTag = "<" + $this.data('tag') + ">";
                        endTag = "</" + $this.data('tag') + ">";
                    } else if ($this.data('tag-selfclosing')){
                        startTag = "<" + $this.data('tag-selfclosing') + "/>";
                    } else if ($this.data('act')) {
                        if ($this.data('act') == 'spec') {
                            addSymbol();
                        }
                        return false;
                    }

                    var myField = textAreaOpened;

                    //IE support
                    if (document.selection) {
                        textAreaOpened.focus();
                        sel = document.selection.createRange();
                        sel.text = startTag + sel.text + endTag;
                    }
                    //MOZILLA/NETSCAPE support
                    else if (textAreaOpened.selectionStart || textAreaOpened.selectionStart == '0') {
                        var startPos = textAreaOpened.selectionStart;
                        var endPos = textAreaOpened.selectionEnd;
                        textAreaOpened.value = textAreaOpened.value.substring(0, startPos)
                            + startTag + textAreaOpened.value.substring(startPos, endPos) + endTag + textAreaOpened.value.substring(endPos, textAreaOpened.value.length);
                    }
                });

                $('.accept-button', $overlay).click(function(){
                    save();
                    $(document).unbind('click.blur-overlay');
                });

                $(document).bind('click.blur-overlay', function(event){
                    if ($(event.target).closest('.html-editarea, #specialCharsContainer').length > 0) {
                        return;
                    }
                    save();
                    $(document).unbind('click.blur-overlay');
                });

            },
            error: function(text){
                alert('Błąd! ' + text);
            }
        });
    }

    function createUwagaBefore(before) {
        xml2html({
            xml: '<uwaga/>',
            success: function(element){
                let $element = $(element);
                $element.insertBefore(before);
                openForEdit($element);
            }
        });
    }

    class VisualPerspective extends $.wiki.Perspective {
        constructor(options) {
            super(options);
            let self = this;
            var element = $("#html-view");
            var button = $('<button class="edit-button active-block-button">Edytuj</button>');
            var uwagaButton = $('<button class="uwaga-button active-block-button">Uwaga</button>');

            if (!CurrentDocument.readonly) {

                $('#html-view').bind('mousemove', function(event){
                    var editable = $(event.target).closest('*[x-editable]');
                    $('.active', element).not(editable).removeClass('active').children('.html-editarea-toolbar').remove();

                    if (!editable.hasClass('active')) {
                        var toolbar = $("<div class='html-editarea-toolbar'><div class='html-editarea-toolbar-left'></div></div>")
                        editable.append(toolbar);
                        var buttonSpace = $('.html-editarea-toolbar-left', toolbar);
                        editable.addClass('active');
                        buttonSpace.append(button);
                        if (!editable.is('[x-edit-attribute]') &&
                            !editable.is('.annotation-inline-box') &&
                            !editable.is('[x-edit-no-format]')
                           ) {
                            buttonSpace.append(uwagaButton);
                        }
                    }
                    if (editable.is('.annotation-inline-box')) {
                        $('*[x-annotation-box]', editable).css({
                        }).show();
                    }
                    if (editable.is('.reference-inline-box')) {
			let preview = $('*[x-preview]', editable);
			preview.show();
			let link = $("a", preview);
			let href = link.attr('href');
			if (link.attr('title') == '?' && href.startsWith('https://www.wikidata.org/wiki/')) {
			    link.attr('title', '…');
			    let qid = href.split('/').reverse()[0];
			    $.ajax({
				url: 'https://www.wikidata.org/w/rest.php/wikibase/v1/entities/items/' + qid + '?_fields=labels',
				dataType: "json",
				success: function(data) {
				    link.attr(
					'title',
					data['labels']['pl'] || data['labels']['en']
				    );
				},
			    });
			}
                    }
                });

                self.caret = new Caret(element);

                $('#insert-reference-button').click(function(){
                    self.flush();
                    self.addReference();
                    return false;
                });

                $('#insert-annotation-button').click(function(){
                    self.flush();
                    addAnnotation();
                    return false;
                });

                $('#insert-theme-button').click(function(){
                    self.flush();
                    addTheme();
                    return false;
                });

                $(".insert-inline-tag").click(function() {
                    self.flush();
                    self.insertInlineTag($(this).attr('data-tag'));
                    return false;
                });

                $(".insert-char").click(function() {
                    self.flush();
                    addSymbol(caret=self.caret);
                    return false;
                });

                $(document).on('click', '.edit-button', function(event){
                    self.flush();
                    event.preventDefault();
                    openForEdit($(this).closest('.html-editarea-toolbar').parent());
                });

                $(document).on('click', '.uwaga-button', function(event){
                    self.flush();
                    event.preventDefault();
                    createUwagaBefore($(this).closest('.html-editarea-toolbar').parent());
                });
            }

            $(document).on('click', '[x-node="motyw"]', function(){
                selectTheme($(this).attr('theme-class'));
            });

            element.on('click', '.annotation', function(event) {
                self.flush();
                event.preventDefault();
                event.redakcja_caret_ignore = true;
                $('[x-annotation-box]', $(this).parent()).toggleClass('editing');
                self.caret.detach();
            });
        }

        onEnter(success, failure) {
            super.onEnter();

            $.blockUI({
                message: 'Uaktualnianie widoku...'
            });

            function _finalize(callback){
                $.unblockUI();
                if (callback)
                    callback();
            }

	    let self = this;
            xml2html({
                xml: this.doc.text,
                base: this.doc.getBase(),
                success: function(element){

                    var htmlView = $('#html-view');
                    htmlView.html(element);
		    self.renumber();
                    if ('PropertiesPerspective' in $.wiki.perspectives)
                        $.wiki.perspectives.PropertiesPerspective.enable();

                    _finalize(success);
                },
                error: function(text, source){
                    let err = '<p class="error">Wystąpił błąd:</p><p>'+text+'</p>';
                    if (source)
                        err += '<pre>'+source.replace(/&/g, '&amp;').replace(/</g, '&lt;')+'</pre>'
                    $('#html-view').html(err);
                    _finalize(failure);
                }
            });
        }

        flush() {
            let self = this;
            return new Promise((resolve, reject) => {
                if ($('#html-view .error').length > 0) {
                    reject()
                } else {
                    //return _finalize(failure);
                    html2text({
                        element: $('#html-view').get(0),
                        stripOuter: true,
                        success: (text) => {
                            self.doc.setText(text);
                            resolve();
                        },
                        error: (text) => {
                            reject(text);
                            //$('#source-editor').html('<p>Wystąpił błąd:</p><pre>' + text + '</pre>');
                        }
                    });
                }
            });
        }

        onExit(success, failure) {
            var self = this;

            self.caret.detach();

            if ('PropertiesPerspective' in $.wiki.perspectives)
                $.wiki.perspectives.PropertiesPerspective.disable();

            self.flush().then(() => {
                success && success();
            }).catch((e) => {
                // TODO report
                console.log('REJECTED!', e);
                failure && failure();
            });
        };

        insertInlineTag(tag) {
            this.caret.detach();
            let self = this;

            let selection = window.getSelection();
            var n = selection.rangeCount;
            if (n != 1 || selection.isCollapsed) {
                window.alert("Nie zaznaczono obszaru");
                return false
            }
            let range = selection.getRangeAt(0);

            // Make sure that:
            // Both ends are in the same x-node container.
            // Both ends are set to text nodes.
            // TODO: That the container is a inline-text container.
            let commonNode = range.endContainer;

            if (commonNode.nodeType == Node.TEXT_NODE) {
                commonNode = commonNode.parentNode;
            }
            let node = range.startContainer;
            if (node.nodeType == Node.TEXT_NODE) {
                node = node.parentNode;
            }
            if (node != commonNode) {
                window.alert("Zły obszar.");
                return false;
            }

            let end;
            if (range.endContainer.nodeType == Node.TEXT_NODE) {
                end = range.endContainer.splitText(range.endOffset);
            } else {
                end = document.createTextNode('');
                let cont = $(range.endContainer).contents();
                if (range.endOffset < cont.length) {
                    range.endContainer.insertBefore(end, cont[range.endOffset])
                } else {
                    range.endContainer.append(end);
                }
            }

            let current;
            if (range.startContainer.nodeType == Node.TEXT_NODE) {
                current = range.startContainer.splitText(range.startOffset);
            } else {
                current = document.createTextNode('');
                let cont = $(range.startContainer).contents();
                if (range.startOffset < cont.length) {
                    range.startContainer.insertBefore(current, cont[range.startOffset])
                } else {
                    startNode.append(current);
                }
            }

            // We will construct a HTML element with the range selected.
            let div = $("<span x-pass-thru='true'>");
            while (current != end) {
                n = current.nextSibling;
                $(current).appendTo(div);
                current = n;
            }

            html2text({
                element: div[0],
                success: function(d) {
                    xml2html({
                        xml: d = '<' + tag + '>' + d + '</' + tag + '>',
                        success: function(html) {
                            // What if no end?
                            node.insertBefore($(html)[0], end);
                            self.flush();
                        }
                    });
                },
                error: function(a, b) {
                    console.log(a, b);
                }
            });
        }

        insertAtRange(range, elem) {
            let self = this;
            let $end = $(range.endContainer);
            if ($end.attr('id') == 'caret') {
                self.caret.insert(elem);
            } else {
                range.insertNode(elem[0]);
            }
        }

        addReference() {
            let self = this;
            var selection = window.getSelection();
            var n = selection.rangeCount;

            // TODO: if no selection, take caret position..
            if (n == 0) {
                window.alert("Nie zaznaczono żadnego obszaru");
                return false;
            }

            var range = selection.getRangeAt(n - 1);
            if (!verifyTagInsertPoint(range.endContainer)) {
                window.alert("Nie można wstawić w to miejsce referencji.");
                return false;
            }

            var tag = $('<span></span>');

            range.collapse(false);
            self.insertAtRange(range, tag);

            xml2html({
                xml: '<ref href=""/>',
                success: function(text){
                    var t = $(text);
                    tag.replaceWith(t);
                    openForEdit(t);
                },
                error: function(){
                    tag.remove();
                    alert('Błąd przy dodawaniu referncji:' + errors);
                }
            })
        }

	renumber() {
	    let number = 0;
            $('#html-view *').each((i, e) => {
		let $e = $(e);
		if ($e.closest('[x-node="abstrakt"]').length) return;
		if ($e.closest('[x-node="nota_red"]').length) return;
		if ($e.closest('[x-annotation-box="true"]').length) return;
		let node = $e.attr('x-node');
		if (node == 'numeracja') {
		    number = 0;
		} else if (['werset', 'akap', 'wers'].includes(node)) {
		    number ++;
		    $e.attr('x-number', number);
		}
	    })
	}
    }

    $.wiki.VisualPerspective = VisualPerspective;

})(jQuery);
