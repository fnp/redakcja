if (!window.console) {
    window.console = {
        log: function(){
        }
    }
}


DEFAULT_PERSPECTIVE = "#VisualPerspective";

$(function()
{
	var tabs = $('ol#tabs li');
	var gallery = null;

	CurrentDocument = new $.wikiapi.WikiDocument("document-meta");
	$.blockUI.defaults.baseZ = 10000;

	function initialize()
	{
		$('.editor').hide();

		/*
		 * TABS
		 */
            $(document).on('click', '#tabs li', function(event, callback) {
            event.preventDefault();
			$.wiki.switchToTab(this);
        });

	    $(document).on('click', '#tabs li > .tabclose', function(event, callback) {
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

				$(window).resize();

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
	initAll( $.makeArray($('#tabs li')), initialize);
	console.log(location.hash);
});
