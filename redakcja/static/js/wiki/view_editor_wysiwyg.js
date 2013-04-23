(function($){

    /* Show theme to the user */
    function selectTheme(themeId){
        var selection = window.getSelection();
        selection.removeAllRanges();

        var range = document.createRange();
        var s = $(".motyw[theme-class='" + themeId + "']")[0];
        var e = $(".end[theme-class='" + themeId + "']")[0];

        if (s && e) {
            range.setStartAfter(s);
            range.setEndBefore(e);
            selection.addRange(range);
        }
    };

    /* Verify insertion port for annotation or theme */
    function verifyTagInsertPoint(node){
        if (node.nodeType == 3) { // Text Node
            node = node.parentNode;
        }

        if (node.nodeType != 1) {
            return false;
        }

        node = $(node);
        var xtype = node.attr('x-node');

        if (!xtype || (xtype.search(':') >= 0) ||
        xtype == 'motyw' ||
        xtype == 'begin' ||
        xtype == 'end') {
            return false;
        }

        // don't allow themes inside annotations
        if (node.closest('[x-node="pe"]').length > 0)
            return false;

        return true;
    }

    /* Convert HTML fragment to plaintext */
    var ANNOT_FORBIDDEN = ['pt', 'pa', 'pr', 'pe', 'begin', 'end', 'motyw'];

    function html2plainText(fragment){
        var text = "";

        $(fragment.childNodes).each(function(){
            if (this.nodeType == 3) // textNode
                text += this.nodeValue;
            else {
                if (this.nodeType == 1 &&
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

        if (n == 0) {
            window.alert("Nie zaznaczono żadnego obszaru");
            return false;
        }

        // for now allow only 1 range
        if (n > 1) {
            window.alert("Zaznacz jeden obszar");
            return false;
        }

        // remember the selected range
        var range = selection.getRangeAt(0);

        if (!verifyTagInsertPoint(range.endContainer)) {
            window.alert("Nie można wstawić w to miejsce przypisu.");
            return false;
        }

        // BUG #273 - selected text can contain themes, which should be omitted from
        // defining term
        var text = html2plainText(range.cloneContents());
        var tag = $('<span></span>');
        range.collapse(false);
        range.insertNode(tag[0]);

        xml2html({
            xml: '<pe><slowo_obce>' + text + '</slowo_obce> --- </pe>',
            success: function(text){
                var t = $(text);
                tag.replaceWith(t);
                openForEdit(t);
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
        if (!verifyTagInsertPoint(range.startContainer)) {
            window.alert("Motyw nie może się zaczynać w tym miejscu.");
            return false;
        }

        if (!verifyTagInsertPoint(range.endContainer)) {
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
                                openForEdit($('.motyw[theme-class=' + id + ']'));
                            }
                        });
                    }
                });
            }
        });
    }

    function addSymbol() {
        if($('div.html-editarea textarea')[0]) {
            var specialCharsContainer = $("<div id='specialCharsContainer'><a href='#' id='specialCharsClose'>Zamknij</a><table id='tableSpecialChars' style='width: 600px;'></table></div>");
                        
            var specialChars = ['Ą','ą','Ć','ć','Ę','ę','Ł','ł','Ń','ń','Ó','ó','Ś','ś','Ż','ż','Ź','ź','Á','á','À','à',
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
            '×','÷','≈','≠','±','≤','≥','∈'];
            var tableContent = "<tr>";
            
            for(var i in specialChars) {
                if(i % 14 == 0 && i > 0) {
                    tableContent += "</tr><tr>";
                }              
                tableContent += "<td><input type='button' class='specialBtn' value='"+specialChars[i]+"'/></td>";              
            }
            
            tableContent += "</tr>";                                   
            $("#content").append(specialCharsContainer);
            
            
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
                var editArea = $('div.html-editarea textarea')[0];
                var insertVal = $(this).val();
                
                // if we want to surround text with quotes
                // not sure if just check if value has length == 2
                
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
                    // if we just want to insert single symbol
                    insertAtCaret(editArea, insertVal);
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
    function openForEdit($origin){
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

        // start edition on this node
        var $overlay = $('<div class="html-editarea"><button class="accept-button">Zapisz</button><button class="delete-button">Usuń</button><button class="tytul-button akap-edit-button">tytuł dzieła</button><button class="wyroznienie-button akap-edit-button">wyróżnienie</button><button class="slowo-button akap-edit-button">słowo obce</button><button class="znak-button akap-edit-button">znak spec.</button><textarea></textarea></div>').css({
            position: 'absolute',
            height: h,
            left: x,
            top: y,
            width: w
        }).appendTo($box[0].offsetParent || $box.parent()).show();
        

        if ($origin.is('.motyw')) {
	    $('.akap-edit-button').remove();
            withThemes(function(canonThemes){
                $('textarea', $overlay).autocomplete(canonThemes, {
                    autoFill: true,
                    multiple: true,
                    selectFirst: true,
                    highlight: false
                });
            })
        }

        if ($origin.is('.motyw')){
            $('.delete-button', $overlay).click(function(){
                if (window.confirm("Czy jesteś pewien, że chcesz usunąć ten motyw ?")) {
                    $('[theme-class=' + $origin.attr('theme-class') + ']').remove();
                    $overlay.remove();
                    $(document).unbind('click.blur-overlay');
                    return false;
                };
            });
        }
        else if($box.is('*[x-annotation-box]')) {
            $('.delete-button', $overlay).click(function(){
                if (window.confirm("Czy jesteś pewien, że chcesz usunąć ten przypis?")) {
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

        html2text({
            element: $box[0],
            stripOuter: true,
            success: function(text){
                $('textarea', $overlay).val($.trim(text));

                setTimeout(function(){
                    $('textarea', $overlay).elastic().focus();
                }, 50);

                function save(argument){
                    var nodeName = $box.attr('x-node') || 'pe';
                    var insertedText = $('textarea', $overlay).val();

                    if ($origin.is('.motyw')) {
                        insertedText = insertedText.replace(/,\s*$/, '');
                    }

                    xml2html({
                        xml: '<' + nodeName + '>' + insertedText + '</' + nodeName + '>',
                        success: function(element){
                            if (nodeName == 'out-of-flow-text') {
                                $(element).children().insertAfter($origin);
                                $origin.remove()
                            }
                            else {
                                $origin.html($(element).html());
                            }
                            $overlay.remove();
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
			var buttonName = this.innerHTML;

			if(buttonName == "słowo obce") {
				startTag = "<slowo_obce>";
				endTag = "</slowo_obce>";
			} else if (buttonName == "wyróżnienie") {
				startTag = "<wyroznienie>";
				endTag = "</wyroznienie>";
			} else if (buttonName == "tytuł dzieła") {
				startTag = "<tytul_dziela>";
				endTag = "</tytul_dziela>";
			} else if(buttonName == "znak spec."){
			    addSymbol();
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

    function VisualPerspective(options){

        var old_callback = options.callback;

        options.callback = function(){
            var element = $("#html-view");
            var button = $('<button class="edit-button">Edytuj</button>');

            if (!CurrentDocument.readonly) {
                $('#html-view').bind('mousemove', function(event){
                    var editable = $(event.target).closest('*[x-editable]');
                    $('.active', element).not(editable).removeClass('active').children('.edit-button').remove();

                    if (!editable.hasClass('active')) {
                        editable.addClass('active').append(button);
                    }
                    if (editable.is('.annotation-inline-box')) {
                        $('*[x-annotation-box]', editable).css({
                            position: 'absolute',
                            left: event.clientX - editable.offset().left + 5,
                            top: event.clientY - editable.offset().top + 5
                        }).show();
                    }
                    else {
                        $('*[x-annotation-box]').hide();
                    }
                });

                $('#insert-annotation-button').click(function(){
                    addAnnotation();
                    return false;
                });

                $('#insert-theme-button').click(function(){
                    addTheme();
                    return false;
                });            

                $('.edit-button').live('click', function(event){
                    event.preventDefault();
                    openForEdit($(this).parent());
                });

            }

            $('.motyw').live('click', function(){
                selectTheme($(this).attr('theme-class'));
            });

            old_callback.call(this);
        };

        $.wiki.Perspective.call(this, options);
    };

    VisualPerspective.prototype = new $.wiki.Perspective();

    VisualPerspective.prototype.freezeState = function(){

    };

    VisualPerspective.prototype.onEnter = function(success, failure){
        $.wiki.Perspective.prototype.onEnter.call(this);

        $.blockUI({
            message: 'Uaktualnianie widoku...'
        });

        function _finalize(callback){
            $.unblockUI();
            if (callback)
                callback();
        }

        xml2html({
            xml: this.doc.text,
            success: function(element){
                var htmlView = $('#html-view');
                htmlView.html(element);
                htmlView.find('*[x-node]').dblclick(function(e) {
                    if($(e.target).is('textarea'))
                        return;
                    var selection = window.getSelection();
                    selection.collapseToStart();
                    selection.modify('extend', 'forward', 'word');
                    e.stopPropagation();
                });
                _finalize(success);
            },
            error: function(text, source){
                err = '<p class="error">Wystąpił błąd:</p><p>'+text+'</p>';
                if (source)
                    err += '<pre>'+source.replace(/&/g, '&amp;').replace(/</g, '&lt;')+'</pre>'
                $('#html-view').html(err);
                _finalize(failure);
            }
        });
    };

    VisualPerspective.prototype.onExit = function(success, failure){
        var self = this;

        $.blockUI({
            message: 'Zapisywanie widoku...'
        });

        function _finalize(callback){
            $.unblockUI();
            if (callback)
                callback();
        }

        if ($('#html-view .error').length > 0)
            return _finalize(failure);

        html2text({
            element: $('#html-view').get(0),
            stripOuter: true,
            success: function(text){
                self.doc.setText(text);
                _finalize(success);
            },
            error: function(text){
                $('#source-editor').html('<p>Wystąpił błąd:</p><pre>' + text + '</pre>');
                _finalize(failure);
            }
        });
    };

    $.wiki.VisualPerspective = VisualPerspective;

})(jQuery);
