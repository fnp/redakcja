
if (!window.console) {
    window.console = {
        log: function(){
        }
    }
}

THEMES = ['Alkohol', 'Ambicja', 'Anioł', 'Antysemityzm', 'Arkadia', 'Artysta', 'Bezdomność', 'Bezpieczeństwo', 'Bieda', 'Bijatyka', 'Błazen', 'Błądzenie', 'Błoto', 'Bogactwo', 'Bóg', 'Brat', 'Bunt', 'Buntownik', 'Burza', 'Car', 'Carpe diem', 'Ciemność', 'Cień', 'Cisza', 'Chciwość', 'Chleb', 'Chłop', 'Choroba', 'Chrystus', 'Chrzest', 'Ciało', 'Cierpienie', 'Cmentarz', 'Cnota', 'Córka', 'Cud', 'Czarownika', 'Czary', 'Czas', 'Czyn', 'Czyściec', 'Dama', 'Danse macabre', 'Deszcz', 'Diabeł', 'Dobro', 'Dom', 'Dorosłość', 'Drzewo', 'Duch', 'Dusza', 'Duma', 'Dworek', 'Dworzanin', 'Dwór', 'Dzieciństwo', 'Dziecko', 'Dziedzictwo', 'Dziewictwo', 'Dźwięk', 'Egzorcyzm', 'Elita', 'Emigrant', 'Fałsz', 'Filozof', 'Fircyk', 'Flirt', 'Głupiec', 'Głupota', 'Głód', 'Gospodarz', 'Gospodyni', 'Gość', 'Gotycyzm', 'Góra', 'Gra', 'Grób', 'Grzech', 'Grzeczność', 'Gwiazda', 'Handel', 'Hańba', 'Historia', 'Honor', 'Idealista', 'Imię', 'Interes', 'Jabłka', 'Jedzenie', 'Jesień', 'Kaleka', 'Kara', 'Karczma', 'Klęska', 'Kłamstwo', 'Kłótnia', 'Kobieta', 'Kobieta demoniczna', 'Kobieta "upadła"', 'Kochanek', 'Kochanek romantyczny', 'Kolonializm', 'Kondycja ludzka', 'Konflikt', 'Konflikt wewnętrzny', 'Koniec świata', 'Koń', 'Korzyść', 'Kot', 'Kradzież', 'Krew', 'Król', 'Krzywda', 'Ksiądz', 'Książka', 'Księżyc', 'Kuchnia', 'Kuszenie', 'Kwiaty', 'Labirynt', 'Las', 'Lato', 'Lekarz', 'Lenistwo', 'List', 'Liberat', 'Los', 'Lud', 'Lustro', 'Łzy', 'Małżeństwo', 'Marzenie', 'Maska', 'Maszyna', 'Matka', 'Matka Boska', 'Mądrość', 'Mąż', 'Melancholia', 'Mędrzec', 'Mężczyzna', 'Miasto', 'Mieszczanin', 'Miłosierdzie', 'Miłość', 'Miłość niespełniona', 'Miłość platoniczna', 'Miłość romantyczna', 'Miłość silniejsza niż śmierć', 'Miłość spełniona', 'Miłość tragiczna', 'Mizoginia', 'Młodość', 'Moda', 'Modlitwa', 'Morderstwo', 'Morze', 'Motyl', 'Mucha', 'Muzyka', 'Narodziny', 'Naród', 'Natura', 'Nauczyciel', 'Nauczycielka', 'Nauka', 'Niebezpieczeństwo', 'Niedziela', 'Niemiec', 'Nienawiść', 'Nieśmiertelność', 'Niewola', 'Noc', 'Nuda', 'Obcy', 'Obłok', 'Obowiązek', 'Obraz świata', 'Obrzędy', 'Obyczaje', 'Obywatel', 'Odrodzenie przez grób', 'Odwaga', 'Ofiara', 'Ogień', 'Ogród', 'Ojciec', 'Ojczyzna', 'Oko', 'Okręt', 'Okrucieństwo', 'Omen', 'Opieka', 'Organizm', 'Otchłań', 'Pająk', 'Pamięć', 'Pan', 'Panna młoda', 'Państwo', 'Patriota', 'Piekło', 'Pielgrzym', 'Pieniądz', 'Pies', 'Piętno', 'Pijaństwo', 'Piwnica', 'Plotka', 'Pobożność', 'Pocałunek', 'Pochlebstwo', 'Poeta', 'Poetka', 'Poezja', 'Podróż', 'Podstęp', 'Pogrzeb', 'Pojedynek', 'Pokora', 'Pokusa', 'Polak', 'Polityka', 'Polowanie', 'Polska', 'Portret', 'Porwanie', 'Poświęcenie', 'Potwór', 'Powstanie', 'Powstaniec', 'Pozory', 'Pozycja społeczna', 'Pożar', 'Pożądanie', 'Praca', 'Praca u podstaw', 'Praca organiczna', 'Prawda', 'Prawnik', 'Prometeusz', 'Proroctwo', 'Prorok', 'Próżność', 'Przebranie', 'Przeczucie', 'Przedmurze chrześcijaństwa', 'Przekleństwo', 'Przekupstwo', 'Przemiana', 'Przemijanie', 'Przemoc', 'Przestrzeń', 'Przyjaźń', 'Przyroda nieożywiona', 'Przysięga', 'Przywódca', 'Ptak', 'Pustynia', 'Pycha', 'Raj', 'Realista', 'Religia', 'Rewolucja', 'Robak', 'Robotnik', 'Rodzina', 'Rosja', 'Rosjanin', 'Rośliny', 'Rozczarowanie', 'Rozpacz', 'Rozstanie', 'Rozum', 'Ruiny', 'Rycerz', 'Rzeka', 'Salon', 'Samobójstwo', 'Samolubstwo', 'Samotnik', 'Samotność', 'Sarmata', 'Sąsiad', 'Sąd', 'Sąd Ostateczny', 'Sen', 'Serce', 'Sędzia', 'Sielanka', 'Sierota', 'Siła', 'Siostra', 'Sława', 'Słońce', 'Słowo', 'Sługa', 'Służalczość', 'Skąpiec', 'Sobowtór', 'Społecznik', 'Spowiedź', 'Sprawiedliwość', 'Starość', 'Strach', 'Strój', 'Stworzenie', 'Sumienie', 'Swaty', 'Syberia', 'Syn', 'Syn marnotrawny', 'Syzyf', 'Szaleniec', 'Szaleństwo', 'Szantaż', 'Szatan', 'Szczęście', 'Szkoła', 'Szlachcic', 'Szpieg', 'Sztuka', 'Ślub', 'Śmiech', 'Śmierć', 'Śmierć bohaterska', 'Śpiew', 'Światło', 'Świętoszek', 'Święty', 'Świt', 'Tajemnica', 'Taniec', 'Tchórzostwo', 'Teatr', 'Testament', 'Tęsknota', 'Theatrum mundi', 'Tłum', 'Trucizna', 'Trup', 'Twórczość', 'Uczeń', 'Uczta', 'Uroda', 'Umiarkowanie', 'Upadek', 'Upiór', 'Urzędnik', 'Vanitas', 'Walka', 'Walka klas', 'Wampir', 'Warszawa', 'Wąż', 'Wdowa', 'Wdowiec', 'Wesele', 'Wiatr', 'Wierność', 'Wierzenia', 'Wieś', 'Wiedza', 'Wieża Babel', 'Więzienie', 'Więzień', 'Wina', 'Wino', 'Wiosna', 'Wizja', 'Władza', 'Własność', 'Woda', 'Wojna', 'Wojna pokoleń', 'Wolność', 'Wróg', 'Wspomnienia', 'Współpraca', 'Wygnanie', 'Wyrzuty sumienia', 'Wyspa', 'Wzrok', 'Zabawa', 'Zabobony', 'Zamek', 'Zaręczyny', 'Zaświaty', 'Zazdrość', 'Zbawienie', 'Zbrodnia', 'Zbrodniarz', 'Zdrada', 'Zdrowie', 'Zemsta', 'Zesłaniec', 'Ziarno', 'Ziemia', 'Zima', 'Zło', 'Złodziej', 'Złoty wiek', 'Zmartwychwstanie', 'Zwątpienie', 'Zwierzęta', 'Zwycięstwo', 'Żałoba', 'Żebrak', 'Żołnierz', 'Żona', 'Życie jako wędrówka', 'Życie snem', 'Żyd', 'Żywioły', 'Oświadczyny']

function gallery(element, url){
    var element = $(element);
    var imageDimensions = {};
    element.data('images', []);
    
    function changePage(pageNumber){
        $('.gallery-image img', element).attr('src', element.data('images')[pageNumber - 1]);
    }
    
    function normalizeNumber(pageNumber){
        // Numer strony musi być pomiędzy 1 a najwyższym numerem
        var pageCount = element.data('images').length;
        pageNumber = parseInt(pageNumber, 10);
        
        if (!pageNumber || pageNumber == NaN || pageNumber == Infinity || pageNumber == -Infinity) {
            return 1;
        }
        else 
            if (pageNumber < 1) {
                return 1;
            }
            else 
                if (pageNumber > pageCount) {
                    return pageCount;
                }
                else {
                    return pageNumber;
                }
    }
    
    var pn = $('.page-number', element);
    pn.change(function(event){
        event.preventDefault();
        var n = normalizeNumber(pn.val());
        pn.val(n);
        changePage(n);
    });
    $('.previous-page', element).click(function(){
        pn.val(normalizeNumber(pn.val()) - 1);
        pn.change();
    });
    $('.next-page', element).click(function(){
        pn.val(normalizeNumber(pn.val()) + 1);
        pn.change();
    });
    
    
    var image = $('.gallery-image img', element).attr('unselectable', 'on');
    var origin = {};
    var imageOrigin = {};
    var zoomFactor = 1;
    
    $('.zoom-in', element).click(function(){
        zoomFactor = Math.min(2, zoomFactor + 0.2);
        zoom();
    });
    $('.zoom-out', element).click(function(){
        zoomFactor = Math.max(0.2, zoomFactor - 0.2);
        zoom();
    });
    $('.change-gallery', element).click(function(){
        $('.chosen-gallery').val($('#document-meta .gallery').html() || '/platforma/gallery/');
        $('.gallery-image').animate({
            top: 60
        }, 200);
        $('.chosen-gallery').focus();
    });
    $('.change-gallery-ok', element).click(function(){
        if ($('#document-meta .gallery').length == 0) {
            $('<div class="gallery"></div>').appendTo('#document-meta');
        }
        $('#document-meta .gallery').html($('.chosen-gallery').val());
        updateGallery($('.chosen-gallery').val());
        $('.gallery-image').animate({
            top: 30
        }, 200);
    });
    $('.change-gallery-cancel', element).click(function(){
        $('.gallery-image').animate({
            top: 30
        }, 200);
    });
    
    $('.gallery-image img', element).load(function(){
        image.css({
            width: null,
            height: null
        });
        imageDimensions = {
            width: $(this).width() * zoomFactor,
            height: $(this).height() * zoomFactor,
            originWidth: $(this).width(),
            originHeight: $(this).height(),
            galleryWidth: $(this).parent().width(),
            galleryHeight: $(this).parent().height()
        };
        
        if (!(imageDimensions.width && imageDimensions.height)) {
            setTimeout(function(){
                $('.gallery-image img', element).load();
            }, 100);
        }
        var position = normalizePosition(image.position().left, image.position().top, imageDimensions.galleryWidth, imageDimensions.galleryHeight, imageDimensions.width, imageDimensions.height);
        image.css({
            left: position.x,
            top: position.y,
            width: $(this).width() * zoomFactor,
            height: $(this).height() * zoomFactor
        });
    });
    
    $(window).resize(function(){
        imageDimensions.galleryWidth = image.parent().width();
        imageDimensions.galleryHeight = image.parent().height();
    });
    
    function bounds(galleryWidth, galleryHeight, imageWidth, imageHeight){
        return {
            maxX: 0,
            maxY: 0,
            minX: galleryWidth - imageWidth,
            minY: galleryHeight - imageHeight
        }
    }
    
    function normalizePosition(x, y, galleryWidth, galleryHeight, imageWidth, imageHeight){
        var b = bounds(galleryWidth, galleryHeight, imageWidth, imageHeight);
        return {
            x: Math.min(b.maxX, Math.max(b.minX, x)),
            y: Math.min(b.maxY, Math.max(b.minY, y))
        }
    }
    
    function onMouseMove(event){
        var position = normalizePosition(event.clientX - origin.x + imageOrigin.left, event.clientY - origin.y + imageOrigin.top, imageDimensions.galleryWidth, imageDimensions.galleryHeight, imageDimensions.width, imageDimensions.height);
        image.css({
            position: 'absolute',
            top: position.y,
            left: position.x
        });
        return false;
    }
    
    function setZoom(factor){
        zoomFactor = factor;
    }
    
    function zoom(){
        imageDimensions.width = imageDimensions.originWidth * zoomFactor;
        imageDimensions.height = imageDimensions.originHeight * zoomFactor;
        var position = normalizePosition(image.position().left, image.position().top, imageDimensions.galleryWidth, imageDimensions.galleryHeight, imageDimensions.width, imageDimensions.height);
        image.css({
            width: imageDimensions.width,
            height: imageDimensions.height,
            left: position.x,
            top: position.y
        });
        
    }
    
    function onMouseUp(event){
        $(document).unbind('mousemove.gallery').unbind('mouseup.gallery');
        return false;
    }
    
    image.bind('mousedown', function(event){
        origin = {
            x: event.clientX,
            y: event.clientY
        };
        imageOrigin = image.position();
        $(document).bind('mousemove.gallery', onMouseMove).bind('mouseup.gallery', onMouseUp);
        return false;
    });
    
    function updateGallery(url){
        $.ajax({
            url: url,
            type: 'GET',
            dataType: 'json',
            
            success: function(data){
                element.data('images', data);
                pn.val(1);
                pn.change();
                $('.gallery-image img', element).show();
            },
            
            error: function(data){
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

$(function() {
    // gallery('#sidebar', $('#document-meta .gallery').html());
	
	var tabs = $('ol#tabs li');		
	var perspectives = {};
	var wikidoc = new $.wikiapi.WikiDocument("document-meta");
	
	function activePerspective() {
		return perspectives[$("#tabs " + document.location.hash + "-tab").attr('data-ui-jsclass')];		
	};
	        
    function initialize() 
	{		
		/* The save button */
        $('#save-button').click(function(event){
            event.preventDefault();
            $.blockUI({
                message: $('#save-dialog')
            });
        });
        
        $('#save-ok').click(function(){
            $.blockUI({
                message: 'Zapisywanie...'
            });
			
			var ap = activePerspective();
			
			/* exit perspective */
			ap.onExit();          
			
			function finalize() {
				ap.onEnter();
				$.unblockUI();
			};
			
			wikidoc.save( $("#komentarz").text(), 
				function(doc, changed) {
					console.log("Saved.");				
					finalize();				
				}, 
				function(doc, message) {
					alert(message);
					finalize();					
				}
			);
        });
        
        $('#save-cancel').click(function(){
            $.unblockUI();
        }); 
				
		$('.editor').hide();   
		
		/*
		 * TABS 
		 */		
        tabs.click(function(event, callback) {
			/* hide old */
            var $old = tabs.filter('.active');
						
			$old.each(function(){
				$(this).removeClass('active');
				$('#' + $(this).attr('data-ui-related')).hide();
				perspectives[$(this).attr('data-ui-jsclass')].onExit();
			});			
			
			/* show new */						
            $(this).addClass('active');
            $('#' + $(this).attr('data-ui-related')).show();			
            perspectives[$(this).attr('data-ui-jsclass')].onEnter();
        });
        		
        
        $(window).resize(function(){
            $('iframe').height($(window).height() - $('#tabs').outerHeight() - $('#source-editor .toolbar').outerHeight());
        });
        
        $(window).resize();
        
        $('.vsplitbar').click(function(){
            if ($('#sidebar').width() == 0) {
                $('#sidebar').width(480).css({
                    right: 0
                }).show();
                $('#editor .editor').css({
                    right: 495
                });
                $('.vsplitbar').css({
                    right: 480
                }).addClass('active');
            }
            else {
                $('#sidebar').width(0).hide();
                $('#editor .editor').css({
                    right: 15
                });
                $('.vsplitbar').css({
                    right: 0
                }).removeClass('active');
            }
            $(window).resize();
        });
        
        $(window).bind('beforeunload', function(event){
            return "Na stronie mogą być zmiany.";
        });
		
		console.log("prepare for fetch");
		
		wikidoc.fetch({
			success: function(){
				console.log("Fetch success");
				$('#loading-overlay').fadeOut();				
				var active_tab = document.location.hash || "#VisualPerspective";
				var $active = $("#tabs " + active_tab + "-tab");
				
				$active.trigger("click");
			},
			failure: function() {
				$('#loading-overlay').fadeOut();
				alert("FAILURE");
			}
		});
						
    }; /* end of initialize() */
	
	var initAll = function(a, f) {				
		if (a.length == 0) return f();	
			
		var klass = a.pop();
		console.log("INIT", klass);		
		var p = new $.wiki[klass](wikidoc, function() {
			perspectives[this.perspective_id] = this;			 
			initAll(a, f); 
		});						
		
	};
	
	/*
	 * Initialize all perspectives 
	 */
	initAll($.makeArray( $('ol#tabs li').map(function(){
			return $(this).attr('data-ui-jsclass');						
	})), initialize);
	
	console.log(location.hash);
	
});
