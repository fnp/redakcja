if (!window.console) {
    window.console = {
        log: function(){
        }
    }
}

var DEFAULT_PERSPECTIVE = "#SummaryPerspective";

THEMES = [
	'Alkohol', 'Ambicja', 'Anioł', 'Antysemityzm', 'Arkadia', 'Artysta', 'Bezdomność', 'Bezpieczeństwo', 'Bieda', 'Bijatyka', 'Błazen', 'Błądzenie', 'Błoto', 'Bogactwo', 'Bóg', 'Brat', 'Bunt', 'Buntownik', 'Burza', 'Car', 'Carpe diem', 'Ciemność', 'Cień', 'Cisza', 'Chciwość', 'Chleb', 'Chłop', 'Choroba', 'Chrystus', 'Chrzest', 'Ciało', 'Cierpienie', 'Cmentarz', 'Cnota', 'Córka', 'Cud', 'Czarownica', 'Czary', 'Czas', 'Czyn', 'Czyściec', 'Dama', 'Danse macabre', 'Deszcz', 'Diabeł', 'Dobro', 'Dom', 'Dorosłość', 'Drzewo', 'Duch', 'Dusza', 'Duma', 'Dworek', 'Dworzanin', 'Dwór', 'Dzieciństwo', 'Dziecko', 'Dziedzictwo', 'Dziewictwo', 'Dźwięk', 'Egzorcyzm', 'Elita', 'Emigrant', 'Fałsz', 'Filozof', 'Fircyk', 'Flirt', 'Głupiec', 'Głupota', 'Głód', 'Gospodarz', 'Gospodyni', 'Gość', 'Gotycyzm', 'Góra', 'Gra', 'Grób', 'Grzech', 'Grzeczność', 'Gwiazda', 'Handel', 'Hańba', 'Historia', 'Honor', 'Idealista', 'Imię', 'Interes', 'Jabłka', 'Jedzenie', 'Jesień', 'Kaleka', 'Kara', 'Karczma', 'Klęska', 'Kłamstwo', 'Kłótnia', 'Kobieta', 'Kobieta demoniczna', 'Kobieta "upadła"', 'Kochanek', 'Kochanek romantyczny', 'Kolonializm', 'Kondycja ludzka', 'Konflikt', 'Konflikt wewnętrzny', 'Koniec świata', 'Koń', 'Korzyść', 'Kot', 'Kradzież', 'Krew', 'Król', 'Krzywda', 'Ksiądz', 'Książka', 'Księżyc', 'Kuchnia', 'Kuszenie', 'Kwiaty', 'Labirynt', 'Las', 'Lato', 'Lekarz', 'Lenistwo', 'List', 'Liberat', 'Los', 'Lud', 'Lustro', 'Łzy', 'Małżeństwo', 'Marzenie', 'Maska', 'Maszyna', 'Matka', 'Matka Boska', 'Mądrość', 'Mąż', 'Melancholia', 'Mędrzec', 'Mężczyzna', 'Miasto', 'Mieszczanin', 'Miłosierdzie', 'Miłość', 'Miłość niespełniona', 'Miłość platoniczna', 'Miłość romantyczna', 'Miłość silniejsza niż śmierć', 'Miłość spełniona', 'Miłość tragiczna', 'Mizoginia', 'Młodość', 'Moda', 'Modlitwa', 'Morderstwo', 'Morze', 'Motyl', 'Mucha', 'Muzyka', 'Narodziny', 'Naród', 'Natura', 'Nauczyciel', 'Nauczycielka', 'Nauka', 'Niebezpieczeństwo', 'Niedziela', 'Niemiec', 'Nienawiść', 'Nieśmiertelność', 'Niewola', 'Noc', 'Nuda', 'Obcy', 'Obłok', 'Obowiązek', 'Obraz świata', 'Obrzędy', 'Obyczaje', 'Obywatel', 'Odrodzenie przez grób', 'Odwaga', 'Ofiara', 'Ogień', 'Ogród', 'Ojciec', 'Ojczyzna', 'Oko', 'Okręt', 'Okrucieństwo', 'Omen', 'Opieka', 'Organizm', 'Otchłań', 'Pająk', 'Pamięć', 'Pan', 'Panna młoda', 'Państwo', 'Patriota', 'Piekło', 'Pielgrzym', 'Pieniądz', 'Pies', 'Piętno', 'Pijaństwo', 'Piwnica', 'Plotka', 'Pobożność', 'Pocałunek', 'Pochlebstwo', 'Poeta', 'Poetka', 'Poezja', 'Podróż', 'Podstęp', 'Pogrzeb', 'Pojedynek', 'Pokora', 'Pokusa', 'Polak', 'Polityka', 'Polowanie', 'Polska', 'Portret', 'Porwanie', 'Poświęcenie', 'Potwór', 'Powstanie', 'Powstaniec', 'Pozory', 'Pozycja społeczna', 'Pożar', 'Pożądanie', 'Praca', 'Praca u podstaw', 'Praca organiczna', 'Prawda', 'Prawnik', 'Prometeusz', 'Proroctwo', 'Prorok', 'Próżność', 'Przebranie', 'Przeczucie', 'Przedmurze chrześcijaństwa', 'Przekleństwo', 'Przekupstwo', 'Przemiana', 'Przemijanie', 'Przemoc', 'Przestrzeń', 'Przyjaźń', 'Przyroda nieożywiona', 'Przysięga', 'Przywódca', 'Ptak', 'Pustynia', 'Pycha', 'Raj', 'Realista', 'Religia', 'Rewolucja', 'Robak', 'Robotnik', 'Rodzina', 'Rosja', 'Rosjanin', 'Rośliny', 'Rozczarowanie', 'Rozpacz', 'Rozstanie', 'Rozum', 'Ruiny', 'Rycerz', 'Rzeka', 'Salon', 'Samobójstwo', 'Samolubstwo', 'Samotnik', 'Samotność', 'Sarmata', 'Sąsiad', 'Sąd', 'Sąd Ostateczny', 'Sen', 'Serce', 'Sędzia', 'Sielanka', 'Sierota', 'Siła', 'Siostra', 'Sława', 'Słońce', 'Słowo', 'Sługa', 'Służalczość', 'Skąpiec', 'Sobowtór', 'Społecznik', 'Spowiedź', 'Sprawiedliwość', 'Starość', 'Strach', 'Strój', 'Stworzenie', 'Sumienie', 'Swaty', 'Syberia', 'Syn', 'Syn marnotrawny', 'Syzyf', 'Szaleniec', 'Szaleństwo', 'Szantaż', 'Szatan', 'Szczęście', 'Szkoła', 'Szlachcic', 'Szpieg', 'Sztuka', 'Ślub', 'Śmiech', 'Śmierć', 'Śmierć bohaterska', 'Śpiew', 'Światło', 'Świętoszek', 'Święty', 'Świt', 'Tajemnica', 'Taniec', 'Tchórzostwo', 'Teatr', 'Testament', 'Tęsknota', 'Theatrum mundi', 'Tłum', 'Trucizna', 'Trup', 'Twórczość', 'Uczeń', 'Uczta', 'Uroda', 'Umiarkowanie', 'Upadek', 'Upiór', 'Urzędnik', 'Vanitas', 'Walka', 'Walka klas', 'Wampir', 'Warszawa', 'Wąż', 'Wdowa', 'Wdowiec', 'Wesele', 'Wiatr', 'Wierność', 'Wierzenia', 'Wieś', 'Wiedza', 'Wieża Babel', 'Więzienie', 'Więzień', 'Wina', 'Wino', 'Wiosna', 'Wizja', 'Władza', 'Własność', 'Woda', 'Wojna', 'Wojna pokoleń', 'Wolność', 'Wróg', 'Wspomnienia', 'Współpraca', 'Wygnanie', 'Wyrzuty sumienia', 'Wyspa', 'Wzrok', 'Zabawa', 'Zabobony', 'Zamek', 'Zaręczyny', 'Zaświaty', 'Zazdrość', 'Zbawienie', 'Zbrodnia', 'Zbrodniarz', 'Zdrada', 'Zdrowie', 'Zemsta', 'Zesłaniec', 'Ziarno', 'Ziemia', 'Zima', 'Zło', 'Złodziej', 'Złoty wiek', 'Zmartwychwstanie', 'Zwątpienie', 'Zwierzęta', 'Zwycięstwo', 'Żałoba', 'Żebrak', 'Żołnierz', 'Żona', 'Życie jako wędrówka', 'Życie snem', 'Żyd', 'Żywioły', 'Oświadczyny'
];

$(function()
{
	var tabs = $('ol#tabs li');
	var gallery = null;
	CurrentDocument = new $.wikiapi.WikiDocument("document-meta");

	$.blockUI.defaults.baseZ = 10000;

    function initialize()
	{
		gallery = new $.wiki.ScanGalleryPerspective({
			doc: CurrentDocument, id: "ScanGalleryPerspective"
		});

		$(document).keydown(function(event) {
			console.log("Received key:", event);
		});

		/* The save button */
        $('#save-button').click(function(event){
            event.preventDefault();
			$.wiki.showDialog('#save_dialog');
        });

		$('.editor').hide();

		/*
		 * TABS
		 */
        $('#tabs li').live('click', function(event, callback) {
			$.wiki.switchToTab(this);
        });

		$('#tabs li > .tabclose').live('click', function(event, callback) {
			var $tab = $(this).parent();

			if($tab.is('.active'))
				$.wiki.switchToTab(DEFAULT_PERSPECTIVE);

			var p = $.wiki.perspectiveForTab($tab);
			p.destroy();

			return false;
        });


        $(window).resize(function(){
            $('iframe').height($(window).height() - $('#tabs').outerHeight() - $('#source-editor .toolbar').outerHeight());
        });

        $(window).resize();

        $('.vsplitbar').toggle(
			function() {
				$.wiki.state.perspectives.ScanGalleryPerspective.show = true;
				$('#side-gallery').show();
				$('.vsplitbar').css('right', 480).addClass('.active');
				$('#editor .editor').css('right', 510);
				$(window).resize();
				gallery.onEnter();
			},
			function() {
				$.wiki.state.perspectives.ScanGalleryPerspective.show = false;
				$('#side-gallery').hide();
				$('.vsplitbar').css('right', 0).removeClass('active');
				$('#editor .editor').css('right', 30);
				$(window).resize();
				gallery.onExit();
			}
		);

		if($.wiki.state.perspectives.ScanGalleryPerspective.show)
			$('.vsplitbar').trigger('click');

        window.onbeforeunload = function(e) {
            if($.wiki.isDirty()) {
				e.returnValue = "Na stronie mogą być nie zapisane zmiany.";
				return "Na stronie mogą być nie zapisane zmiany.";
			};
        };
        
		console.log("Fetching document's text");

		$(document).bind('wlapi_document_changed', function(event, doc) {
			try {
				$('#document-revision').text(doc.revision);
			} catch(e) {
				console.log("Failed handler", e);
			}
		});

		CurrentDocument.fetch({
			success: function(){
				console.log("Fetch success");
				$('#loading-overlay').fadeOut();
				var active_tab = document.location.hash || DEFAULT_PERSPECTIVE;

				if(active_tab == "#ScanGalleryPerspective")
					active_tab = DEFAULT_PERSPECTIVE;

				console.log("Initial tab is:", active_tab)
				$.wiki.switchToTab(active_tab);
			},
			failure: function() {
				$('#loading-overlay').fadeOut();
				alert("FAILURE");
			}
		});
    }; /* end of initialize() */


	/* Load configuration */
	$.wiki.loadConfig();

	var initAll = function(a, f) {
		if (a.length == 0) return f();

		$.wiki.initTab({
			tab: a.pop(),
			doc: CurrentDocument,
			callback: function(){
				initAll(a, f);
			}
		});
	};


	/*
	 * Initialize all perspectives
	 */
	initAll( $.makeArray($('ol#tabs li')), initialize);
	console.log(location.hash);
});
