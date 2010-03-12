if (!window.console) {
    window.console = {
        log: function() {}
    }
}

THEMES = ['Alkohol', 'Ambicja', 'Anioł', 'Antysemityzm', 'Arkadia', 'Artysta', 'Bezdomność',
'Bezpieczeństwo', 'Bieda', 'Bijatyka', 'Błazen', 'Błądzenie', 'Błoto', 'Bogactwo', 'Bóg', 'Brat',
'Bunt', 'Buntownik', 'Burza', 'Car', 'Carpe diem', 'Ciemność', 'Cień', 'Cisza', 'Chciwość', 'Chleb',
'Chłop', 'Choroba', 'Chrystus', 'Chrzest', 'Ciało', 'Cierpienie', 'Cmentarz', 'Cnota', 'Córka', 'Cud',
'Czarownika', 'Czary', 'Czas', 'Czyn', 'Czyściec', 'Dama', 'Danse macabre', 'Deszcz', 'Diabeł',
'Dobro', 'Dom', 'Dorosłość', 'Drzewo', 'Duch', 'Dusza', 'Duma', 'Dworek', 'Dworzanin', 'Dwór',
'Dzieciństwo', 'Dziecko', 'Dziedzictwo', 'Dziewictwo', 'Dźwięk', 'Egzorcyzm', 'Elita', 'Emigrant',
'Fałsz', 'Filozof', 'Fircyk', 'Flirt', 'Głupiec', 'Głupota', 'Głód', 'Gospodarz', 'Gospodyni', 'Gość',
'Gotycyzm', 'Góra', 'Gra', 'Grób', 'Grzech', 'Grzeczność', 'Gwiazda', 'Handel', 'Hańba', 'Historia',
'Honor', 'Idealista', 'Imię', 'Interes', 'Jabłka', 'Jedzenie', 'Jesień', 'Kaleka', 'Kara', 'Karczma',
'Klęska', 'Kłamstwo', 'Kłótnia', 'Kobieta', 'Kobieta demoniczna', 'Kobieta "upadła"', 'Kochanek',
'Kochanek romantyczny', 'Kolonializm', 'Kondycja ludzka', 'Konflikt', 'Konflikt wewnętrzny', 'Koniec świata',
'Koń', 'Korzyść', 'Kot', 'Kradzież', 'Krew', 'Król', 'Krzywda', 'Ksiądz', 'Książka',
'Księżyc', 'Kuchnia', 'Kuszenie', 'Kwiaty', 'Labirynt', 'Las', 'Lato', 'Lekarz', 'Lenistwo', 'List',
'Liberat', 'Los', 'Lud', 'Lustro', 'Łzy', 'Małżeństwo', 'Marzenie', 'Maska', 'Maszyna', 'Matka',
'Matka Boska', 'Mądrość', 'Mąż', 'Melancholia', 'Mędrzec', 'Mężczyzna', 'Miasto', 'Mieszczanin',
'Miłosierdzie', 'Miłość', 'Miłość niespełniona', 'Miłość platoniczna', 'Miłość romantyczna', 
'Miłość silniejsza niż śmierć', 'Miłość spełniona', 'Miłość tragiczna', 'Mizoginia', 'Młodość', 'Moda',
'Modlitwa', 'Morderstwo', 'Morze', 'Motyl', 'Mucha', 'Muzyka', 'Narodziny', 'Naród', 'Natura',
'Nauczyciel', 'Nauczycielka', 'Nauka', 'Niebezpieczeństwo', 'Niedziela', 'Niemiec', 'Nienawiść',
'Nieśmiertelność', 'Niewola', 'Noc', 'Nuda', 'Obcy', 'Obłok', 'Obowiązek', 'Obraz świata', 'Obrzędy',
'Obyczaje', 'Obywatel', 'Odrodzenie przez grób', 'Odwaga', 'Ofiara', 'Ogień', 'Ogród', 'Ojciec',
'Ojczyzna', 'Oko', 'Okręt', 'Okrucieństwo', 'Omen', 'Opieka', 'Organizm', 'Otchłań', 'Pająk', 'Pamięć',
'Pan', 'Panna młoda', 'Państwo', 'Patriota', 'Piekło', 'Pielgrzym', 'Pieniądz', 'Pies', 'Piętno',
'Pijaństwo', 'Piwnica', 'Plotka', 'Pobożność', 'Pocałunek', 'Pochlebstwo', 'Poeta', 'Poetka', 'Poezja',
'Podróż', 'Podstęp', 'Pogrzeb', 'Pojedynek', 'Pokora', 'Pokusa', 'Polak', 'Polityka', 'Polowanie',
'Polska', 'Portret', 'Porwanie', 'Poświęcenie', 'Potwór', 'Powstanie', 'Powstaniec', 'Pozory',
'Pozycja społeczna', 'Pożar', 'Pożądanie', 'Praca', 'Praca u podstaw', 'Praca organiczna', 'Prawda', 'Prawnik',
'Prometeusz', 'Proroctwo', 'Prorok', 'Próżność', 'Przebranie', 'Przeczucie', 'Przedmurze chrześcijaństwa',
'Przekleństwo', 'Przekupstwo', 'Przemiana', 'Przemijanie', 'Przemoc', 'Przestrzeń',
'Przyjaźń', 'Przyroda nieożywiona', 'Przysięga', 'Przywódca', 'Ptak', 'Pustynia', 'Pycha', 'Raj',
'Realista', 'Religia', 'Rewolucja', 'Robak', 'Robotnik', 'Rodzina', 'Rosja', 'Rosjanin', 'Rośliny',
'Rozczarowanie', 'Rozpacz', 'Rozstanie', 'Rozum', 'Ruiny', 'Rycerz', 'Rzeka', 'Salon', 'Samobójstwo',
'Samolubstwo', 'Samotnik', 'Samotność', 'Sarmata', 'Sąsiad', 'Sąd', 'Sąd Ostateczny', 'Sen', 'Serce',
'Sędzia', 'Sielanka', 'Sierota', 'Siła', 'Siostra', 'Sława', 'Słońce', 'Słowo', 'Sługa', 'Służalczość',
'Skąpiec', 'Sobowtór', 'Społecznik', 'Spowiedź', 'Sprawiedliwość', 'Starość', 'Strach', 'Strój',
'Stworzenie', 'Sumienie', 'Swaty', 'Syberia', 'Syn', 'Syn marnotrawny', 'Syzyf', 'Szaleniec',
'Szaleństwo', 'Szantaż', 'Szatan', 'Szczęście', 'Szkoła', 'Szlachcic', 'Szpieg', 'Sztuka', 'Ślub',
'Śmiech', 'Śmierć', 'Śmierć bohaterska', 'Śpiew', 'Światło', 'Świętoszek', 'Święty', 'Świt',
'Tajemnica', 'Taniec', 'Tchórzostwo', 'Teatr', 'Testament', 'Tęsknota', 'Theatrum mundi', 'Tłum',
'Trucizna', 'Trup', 'Twórczość', 'Uczeń', 'Uczta', 'Uroda', 'Umiarkowanie', 'Upadek', 'Upiór',
'Urzędnik', 'Vanitas', 'Walka', 'Walka klas', 'Wampir', 'Warszawa', 'Wąż', 'Wdowa', 'Wdowiec',
'Wesele', 'Wiatr', 'Wierność', 'Wierzenia', 'Wieś', 'Wiedza', 'Wieża Babel', 'Więzienie', 'Więzień',
'Wina', 'Wino', 'Wiosna', 'Wizja', 'Władza', 'Własność', 'Woda', 'Wojna', 'Wojna pokoleń', 'Wolność',
'Wróg', 'Wspomnienia', 'Współpraca', 'Wygnanie', 'Wyrzuty sumienia', 'Wyspa', 'Wzrok', 'Zabawa',
'Zabobony', 'Zamek', 'Zaręczyny', 'Zaświaty', 'Zazdrość', 'Zbawienie', 'Zbrodnia', 'Zbrodniarz',
'Zdrada', 'Zdrowie', 'Zemsta', 'Zesłaniec', 'Ziarno', 'Ziemia', 'Zima', 'Zło', 'Złodziej', 'Złoty wiek',
'Zmartwychwstanie', 'Zwątpienie', 'Zwierzęta', 'Zwycięstwo', 'Żałoba', 'Żebrak', 'Żołnierz',
'Żona', 'Życie jako wędrówka', 'Życie snem', 'Żyd', 'Żywioły', 'Oświadczyny']


// Teraz nieużywane
function highlight(colour) {
    var range, sel;
    if (window.getSelection) {
        // Non-IE case
        sel = window.getSelection();
        if (sel.getRangeAt) {
            range = sel.getRangeAt(0);
        }
        document.designMode = "on";
        if (range) {
            sel.removeAllRanges();
            sel.addRange(range);
        }
        // Use HiliteColor since some browsers apply BackColor to the whole block
        if ( !document.execCommand("HiliteColor", false, colour) ) {
            document.execCommand("BackColor", false, colour);
        }
        document.designMode = "off";
    } else if (document.selection && document.selection.createRange) {
        // IE case
        range = document.selection.createRange();
        range.execCommand("BackColor", false, colour);
    }
}

// function unselectThemes(themeId) {
//     $('.Apple-style-span').each(function() {
//         $(this).after($(this).html());
//         $(this).remove();
//     });
// }

function gallery(element, url) {    
    var element = $(element);
    var imageDimensions = {};
    element.data('images', []);
    
    function changePage(pageNumber) {        
        $('.gallery-image img', element).attr('src', element.data('images')[pageNumber - 1]);
    }
    
    function normalizeNumber(pageNumber) {
        // Numer strony musi być pomiędzy 1 a najwyższym numerem
        var pageCount = element.data('images').length;
        pageNumber = parseInt(pageNumber, 10);
        
        if (!pageNumber || pageNumber == NaN || pageNumber == Infinity || pageNumber == -Infinity) {
            return 1;
        } else if (pageNumber < 1) {
            return 1;
        } else if (pageNumber > pageCount) {
            return pageCount;
        } else {
            return pageNumber;
        }
    }
    
    var pn = $('.page-number', element);
    pn.change(function(event) {
        event.preventDefault();
        var n = normalizeNumber(pn.val());
        pn.val(n);
        changePage(n);
    });
    $('.previous-page', element).click(function() {
        pn.val(normalizeNumber(pn.val()) - 1);
        pn.change();
    });
    $('.next-page', element).click(function() {
        pn.val(normalizeNumber(pn.val()) + 1);
        pn.change();
    });
    
    
    var image = $('.gallery-image img', element).attr('unselectable', 'on');
    var origin = {};
    var imageOrigin = {};
    var zoomFactor = 1;
    
    $('.zoom-in', element).click(function() {
        zoomFactor = Math.min(2, zoomFactor + 0.2);
        zoom();
    });
    $('.zoom-out', element).click(function() {
        zoomFactor = Math.max(0.2, zoomFactor - 0.2);
        zoom();
    });
    $('.change-gallery', element).click(function() {
        $('.chosen-gallery').val($('#document-meta .gallery').html() || '/platforma/gallery/');
        $('.gallery-image').animate({top: 60}, 200);
        $('.chosen-gallery').focus();
    });
    $('.change-gallery-ok', element).click(function() {
        if ($('#document-meta .gallery').length == 0) {
            $('<div class="gallery"></div>').appendTo('#document-meta');
        }
        $('#document-meta .gallery').html($('.chosen-gallery').val());
        updateGallery($('.chosen-gallery').val());
        $('.gallery-image').animate({top: 30}, 200);
    });
    $('.change-gallery-cancel', element).click(function() {
        $('.gallery-image').animate({top: 30}, 200);
    });
    
    $('.gallery-image img', element).load(function() {
        image.css({width: null, height: null});
        imageDimensions = {
            width: $(this).width() * zoomFactor,
            height: $(this).height() * zoomFactor,
            originWidth: $(this).width(),
            originHeight: $(this).height(),
            galleryWidth: $(this).parent().width(),
            galleryHeight: $(this).parent().height()
        };
        
        if (!(imageDimensions.width && imageDimensions.height)) {
            setTimeout(function() { $('.gallery-image img', element).load(); }, 100);
        }        
        var position = normalizePosition(
            image.position().left,
            image.position().top, 
            imageDimensions.galleryWidth,
            imageDimensions.galleryHeight,
            imageDimensions.width,
            imageDimensions.height
        );
        image.css({left: position.x, top: position.y, width: $(this).width() * zoomFactor, height: $(this).height() * zoomFactor});
    });

    $(window).resize(function() {
        imageDimensions.galleryWidth = image.parent().width();
        imageDimensions.galleryHeight = image.parent().height();
    });
    
    function bounds(galleryWidth, galleryHeight, imageWidth, imageHeight) {
        return {
            maxX: 0,
            maxY: 0,
            minX: galleryWidth - imageWidth,
            minY: galleryHeight - imageHeight
        }
    }
    
    function normalizePosition(x, y, galleryWidth, galleryHeight, imageWidth, imageHeight) {
        var b = bounds(galleryWidth, galleryHeight, imageWidth, imageHeight);
        return {
            x: Math.min(b.maxX, Math.max(b.minX, x)),
            y: Math.min(b.maxY, Math.max(b.minY, y))
        }
    }
    
    function onMouseMove(event) {
        var position = normalizePosition(
            event.clientX - origin.x + imageOrigin.left,
            event.clientY - origin.y + imageOrigin.top, 
            imageDimensions.galleryWidth,
            imageDimensions.galleryHeight,
            imageDimensions.width,
            imageDimensions.height
        );
        image.css({position: 'absolute', top: position.y, left: position.x});
        return false;
    }
    
    function setZoom(factor) {
        zoomFactor = factor;
    }
    
    function zoom() {
        imageDimensions.width = imageDimensions.originWidth * zoomFactor;
        imageDimensions.height = imageDimensions.originHeight * zoomFactor;
        var position = normalizePosition(
            image.position().left,
            image.position().top, 
            imageDimensions.galleryWidth,
            imageDimensions.galleryHeight,
            imageDimensions.width,
            imageDimensions.height
        );
        image.css({width: imageDimensions.width, height: imageDimensions.height,
            left: position.x, top: position.y});

    }
    
    function onMouseUp(event) {
        $(document)
            .unbind('mousemove.gallery')
            .unbind('mouseup.gallery');
        return false;
    }
    
    image.bind('mousedown', function(event) {
        origin = {
            x: event.clientX,
            y: event.clientY
        };
        imageOrigin = image.position();
        $(document)
            .bind('mousemove.gallery', onMouseMove)
            .bind('mouseup.gallery', onMouseUp);
        return false;
    });
    
    function updateGallery(url) {
        $.ajax({
            url: url,
            type: 'GET',
            dataType: 'json',

            success: function(data) {
                element.data('images', data);
                pn.val(1);
                pn.change();
                $('.gallery-image img', element).show();
            },
            
            error: function(data) {
                element.data('images', []);
                pn.val(1);
                pn.change();
                $('.gallery-image img', element).hide();
            }
        });
    }
    
    if (url) {
        updateGallery(url);
    }
}


function transform(editor, callback) {
    if (!callback) {
        $.blockUI({message: 'Ładowanie...'});
    }
    setTimeout(function() {
        xml2html({
            xml: editor.getCode(),
            success: function(element) {
                $('#html-view').html(element);
                $.unblockUI();
                if (callback) {
                    callback();
                }
            }, error: function(text) {
				var message = $('<pre></pre>');
				message.text(text);
                $('#html-view').html('<p class="error">Wystąpił błąd:</p><pre>' + 
				    message.html() + '</pre>');
					
                $.unblockUI();
                if (callback) {
                    callback();
                }
            }
        });
    }, 200);
};


function reverseTransform(editor, cont, errorCont, dontBlock) {
    var serializer = new XMLSerializer();
    if ($('#html-view .error').length > 0) {
        if (errorCont) {
            errorCont();
        }
        return;
    }
    if (!dontBlock) {
        $.blockUI({message: 'Ładowanie...'});
    }
    setTimeout(function() {
        html2text({
			element: $('#html-view div').get(0),            
            success: function(text) {
                editor.setCode(text);
                if (!dontBlock) {
                    $.unblockUI();
                }
                if (cont) {
                    cont();
                }
            }, error: function(text) {
                $('#source-editor').html('<p>Wystąpił błąd:</p><pre>' + text + '</pre>');
                if (!dontBlock) {
                    $.unblockUI();
                }
                if (errorCont) {
                    errorCont();
                }
            }
        });
    }, 200);
}


// =============
// = HTML View =
// =============
function html(element) {
    var element = $(element);
    
    function selectTheme(themeId)
    {
        var selection = window.getSelection();
        selection.removeAllRanges();

        var range = document.createRange();
        var s = $(".motyw[theme-class='"+themeId+"']")[0];
        var e = $(".end[theme-class='"+themeId+"']")[0];

        if(s && e) {
            range.setStartAfter(s);
            range.setEndBefore(e);
            selection.addRange(range);
        }
    };
    
    function verifyTagInsertPoint(node) {
        if(node.nodeType == 3) { // Text Node
            node = node.parentNode;
        }

        if (node.nodeType != 1) { 
            return false;
        }

        node = $(node);
        var xtype = node.attr('x-node');

        if (!xtype || (xtype.search(':') >= 0) ||
            xtype == 'motyw' || xtype == 'begin' || xtype == 'end') {
            return false;
        }
        
        // don't allow themes inside annotations
        if( node.is('*[x-annotation-box] *') )
            return false;

        return true;
    }
	
	var ANNOT_ALLOWED = ['wyroznienie'];
	
	function html2plainText(fragment) {
		var text = "";
		
		$(fragment.childNodes).each(function() {
			if(this.nodeType == 3) // textNode
			    text += this.nodeValue;
			else if (this.nodeType == 1 
			    && $.inArray($(this).attr('x-node'), ANNOT_ALLOWED) != -1 ){
				text += html2plainText(this);				
			}			
		});
		
		return text;		
	}
    
    function addAnnotation()
    {
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

		// BUG #273 - selected text can contain themes, which should be omited from
		// defining term
        var text = html2plainText( range.cloneContents() ); 
		
        var tag = $('<span></span>');
        range.collapse(false);
        range.insertNode(tag[0]);

        xml2html({
            xml: '<pr><slowo_obce>'+text+'</slowo_obce> --- </pr>',
            success: function(text) {
                var t = $(text);
                tag.replaceWith(t);
                openForEdit(t);
            },
            error: function() {
                tag.remove();
                alert('Błąd przy dodawaniu przypisu:' + errors);                
            }
        })
    }
    
    function addTheme()
    {
        var selection = window.getSelection();
        var n = selection.rangeCount;

        if(n == 0) {
            window.alert("Nie zaznaczono żadnego obszaru");
            return false;
        }

        // for now allow only 1 range
        if(n > 1) {
            window.alert("Zaznacz jeden obszar.");
            return false;
        }
		 

        // remember the selected range
        var range = selection.getRangeAt(0);
		
		
		if( $(range.startContainer).is('.html-editarea') 
		 || $(range.endContainer).is('.html-editarea') ) {
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
        var random = Math.floor(4000000000*Math.random());
        var id = (''+date) + '-' + (''+random);

        var spoint = document.createRange();
        var epoint = document.createRange();

        spoint.setStart(range.startContainer, range.startOffset);
        epoint.setStart(range.endContainer, range.endOffset);

        var mtag, btag, etag, errors;

        // insert theme-ref
                
        xml2html({
            xml: '<end id="e'+id+'" />',
            success: function(text) {
                etag = $('<span></span>');
                epoint.insertNode(etag[0]);
                etag.replaceWith(text);
                xml2html({
                    xml: '<motyw id="m'+id+'"></motyw>',
                    success: function(text) {						
                        mtag = $('<span></span>');
                        spoint.insertNode(mtag[0]);
                        mtag.replaceWith(text);
                        xml2html({
                            xml: '<begin id="b'+id+'" />',
                            success: function(text) {
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
    
    function openForEdit($origin)
    {       
        var $box = null
    
        // annotations overlay their sub box - not their own box //
        if($origin.is(".annotation-inline-box")) {
            $box = $("*[x-annotation-box]", $origin);
        } else {
            $box = $origin;
        }
        
        var x = $box[0].offsetLeft;
        var y = $box[0].offsetTop;
        var w = $box.outerWidth();
        var h = $box.innerHeight();
    
        if ($origin.is(".annotation-inline-box")) {
            w = Math.max(w, 400);
            h = Math.max(h, 60);
        }
        
        // start edition on this node
        var $overlay = $('<div class="html-editarea"><button class="accept-button">Zapisz</button><button class="delete-button">Usuń</button><textarea></textarea></div>').css({
            position: 'absolute',
            height: h,
            left: x,
            top: y,
            width: w
        }).appendTo($box[0].offsetParent || $box.parent()).show();
        
        if ($origin.is('.motyw')) {
            $('textarea', $overlay).autocomplete(THEMES, {
                autoFill: true,
                multiple: true,
                selectFirst: true
            });
        }
        
        $('.delete-button', $overlay).click(function() {
            if ($origin.is('.motyw')) {
                $('[theme-class=' + $origin.attr('theme-class') + ']').remove();
            } else {
                $origin.remove();
            }
            $overlay.remove();
            $(document).unbind('click.blur-overlay');
            return false;
        })
        
        
        var serializer = new XMLSerializer();
        
        html2text({
            element: $box[0],
            stripOuter: true,
            success: function(text) {
                $('textarea', $overlay).val($.trim(text));
                
                setTimeout(function() {
                    $('textarea', $overlay).elastic().focus();
                }, 50);
                
                function save(argument) {
                    var nodeName = $box.attr('x-node') || 'pe';
					var insertedText = $('textarea', $overlay).val();
					
					if ($origin.is('.motyw')) {
						insertedText = insertedText.replace(/,\s*$/, '');
					}
					
                    xml2html({
                        xml: '<' + nodeName + '>' + insertedText + '</' + nodeName + '>',
                        success: function(element) {
                            $box.html($(element).html());
                            $overlay.remove();
                        },
                        error: function(text) {
                            $overlay.remove();
                            alert('Błąd! ' + text);
                        }
                    })
                }
                
                $('.accept-button', $overlay).click(function() {
                    save();
                });
                
                $(document).bind('click.blur-overlay', function(event) {
                    if ($(event.target).parents('.html-editarea').length > 0) {
                        return;
                    }
                    save();
                    
                    $(document).unbind('click.blur-overlay');
                });
                
            }, error: function(text) {
                alert('Błąd! ' + text);
            }
        });
    }
    
    $('.edit-button').live('click', function(event) {
        event.preventDefault();
        openForEdit($(this).parent());
    });
    

    
    var button = $('<button class="edit-button">Edytuj</button>');
    $(element).bind('mousemove', function(event) {
        var editable = $(event.target).closest('*[x-editable]');
        $('.active[x-editable]', element).not(editable).removeClass('active').children('.edit-button').remove();
        if (!editable.hasClass('active')) {
            editable.addClass('active').append(button);
        }
        if (editable.is('.annotation-inline-box')) {
            $('*[x-annotation-box]', editable)
                .css({width: 300, position: 'absolute', left: event.clientX - editable.offset().left + 5, top: event.clientY - editable.offset().top + 5})
                .show();
        } else {
            $('*[x-annotation-box]').hide();
        }
    });

    $('.motyw').live('click', function() {
        selectTheme($(this).attr('theme-class'));
    });
    
    $('#insert-annotation-button').click(function() {
        addAnnotation();
        return false;
    });
    
    $('#insert-theme-button').click(function() {
        addTheme();
        return false;
    });
}

/*
 * History
 */

function refreshHistory(callback){
	$.blockUI({
		message: 'Odświeżanie historii...'
	});
	
	$.ajax({
		url: document.location.href + '/history',
        dataType: 'json',
		error: function() {
			$('#history-view .message-box').html('Nie udało się odświeżyć historii').show();
			$.unblockUI();		
		},
		success: function(data) {
			$('#history-view .message-box').hide();
			var changes_list = $('#changes-list');
			changes_list.html('');
			
			$.each(data, function() {
				var val = this[0];
				changes_list.append('<tr>'
					+'<td><input type="radio" name="rev_from" value="'+val+'">'
						+ '<input type="radio" name="rev_to" value="'+val+'">'
					+'<td>'+ this[0]+'</td>'
					+'<td>'+ this[3]+'</td>'
					+'<td>'+ this[2]+'</td>'
					+'<td>'+ this[1]+'</td></tr>')			
			});							
			$.unblockUI();	
			callback();
		}
	});
};

function historyDiff(callback) {
	var changelist = $('#changes-list');
	var rev_a = $("input[name='rev_from']:checked", changelist);
	var rev_b = $("input[name='rev_to']:checked", changelist);
	
	if (rev_a.length != 1 || rev_b.length != 1) {
		window.alert("Musisz zaznaczyć dwie wersje do porównania.");
		return false;
	}
	
	if (rev_a.val() == rev_b.val()) {
		window.alert("Musisz zaznaczyć dwie różne wersje do porównania.");
		return false;
	}
			
	$.blockUI({
		message: 'Wczytywanie porównania...'
	});
	
	$.ajax({
		url: document.location.href + '/diff/'+rev_a.val() + '/'+ rev_b.val(),
        dataType: 'html',
		error: function() {
			$.unblockUI();
			window.alert('Nie udało się wykonać porównania :(.')					
		},
		success: function(data) {
			$.unblockUI();			
			var diffview = $('#diff-view');			
			diffview.html(data);
			diffview.show();							
		}
	});
}
	

$(function() {
    gallery('#sidebar', $('#document-meta .gallery').html());
    html('#html-view');
    
    CodeMirror.fromTextArea('id_text', {
        parserfile: 'parsexml.js',
        path: STATIC_URL + "js/lib/codemirror/",
        stylesheet: STATIC_URL + "css/xmlcolors.css",
        parserConfig: {
            useHTMLKludges: false
        },
        iframeClass: 'xml-iframe',
        textWrapping: true,
		/* lineNumbers: true, */
        tabMode: 'spaces',
        indentUnit: 0,
        initCallback: function(editor) {
            $('#save-button').click(function(event) {
                event.preventDefault();
                $.blockUI({message: $('#save-dialog')});
            });
            
            $('#save-ok').click(function() {
                $.blockUI({message: 'Zapisywanie...'});
                
                function doSave (argument) {
                    var metaComment = '<!--';
                    $('#document-meta div').each(function() {
                        metaComment += '\n\t' + $(this).attr('class') + ': ' + $(this).html();
                    });
                    metaComment += '\n-->'

                    var data = {
                        name: $('#document-name').html(),
                        text: metaComment + editor.getCode(),
                        revision: $('#document-revision').html(),
                        author: $('#username').html() || 'annonymous',
                        comment: $('#komentarz').val()
                    };

                    $.ajax({
                        url: document.location.href,
                        type: "POST",
                        dataType: "json",
                        data: data,                
                        success: function(data) {
                            if (data.text) {
                                editor.setCode(data.text);
                                $('#document-revision').html(data.revision);
                            } else {
                                alert(data.errors);
                            }
                            $.unblockUI();
                        },
                        error: function(xhr, textStatus, errorThrown) {
                            alert('error: ' + textStatus + ' ' + errorThrown);
                        },
                    })
                }
                
                if ($('#simple-view-tab').hasClass('active')) {
                    reverseTransform(editor, doSave);
                } else {
                    doSave();
                }
            });
            
            $('#save-cancel').click(function() {
                $.unblockUI();
            });
            			
            var tabs = $('ol#tabs li');
			
			tabs.click(function(event, callback) {
				tabs.removeClass('active');
				$('.editor').hide();
				$(this).addClass('active');
				$('#' + $(this).attr('ui:related')).show();				
				$(this).trigger('wl:tabload', callback);								
			});	
			
			
            $('#simple-view-tab').bind('wl:tabload', function(event, callback) {
                transform(editor, callback);
            });
			
			$('#source-view-tab').bind('wl:tabload', function(event, callback) {
                reverseTransform(editor, callback);
            });			                
			
			$('#history-view-tab').bind('wl:tabload', function(event, callback) {
				refreshHistory(callback);								
			}); 
			
			$('#make-diff-button').click(historyDiff);

            $('#source-editor .toolbar button').click(function(event) {
                event.preventDefault();
                var params = eval("(" + $(this).attr('ui:action-params') + ")");
                scriptletCenter.scriptlets[$(this).attr('ui:action')](editor, params);
            });			

            $('.toolbar select').change(function(event) {
                var slug = $(this).val();

                $('.toolbar-buttons-container').hide().filter('[data-group=' + slug + ']').show();
                $(window).resize();
            });

            $('.toolbar-buttons-container').hide();
            $('.toolbar select').change();

			
			$('#simple-view-tab').trigger('click', 
				function() { 
					$('#loading-overlay').fadeOut();
					return false; 
				});            
        }
    });
    
    $(window).resize(function() {
        $('iframe').height($(window).height() - $('#tabs').outerHeight() - $('#source-editor .toolbar').outerHeight());
    });
    
    $(window).resize();
    
    $('.vsplitbar').click(function() {
        if ($('#sidebar').width() == 0) {
            $('#sidebar').width(480).css({right: 0}).show();
            $('#source-editor, #simple-editor').css({right: 495});
            $('.vsplitbar').css({right: 480}).addClass('active');
        } else {
            $('#sidebar').width(0).hide();
            $('#source-editor, #simple-editor').css({right: 15});
            $('.vsplitbar').css({right: 0}).removeClass('active');
        }
        $(window).resize();
    });
                

});
