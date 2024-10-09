if (!window.console) {
    window.console = {
        log: function(){
        }
    }
}

var DEFAULT_PERSPECTIVE = "#VisualPerspective";

$(function() {
    var tabs = $('ol#tabs li');
    var gallery = null;
    var MIN_SIDEBAR_WIDTH = 50,
        DEFAULT_SIDEBAR_WIDTH = 480;

    CurrentDocument = new $.wikiapi.WikiDocument("document-meta");

    $.blockUI.defaults.baseZ = 10000;

    function initialize() {
        var splitter = $('#splitter'),
            vsplitbar = $('#vsplitbar'),
            sidebar = $('#sidebar'),
            dragLayer = $('#drag-layer'),
            vsplitbarWidth = vsplitbar.outerWidth(),
            isHolding = false;

        function setSidebarWidth(x) {
            if (x < MIN_SIDEBAR_WIDTH) {
                x = 0;
                vsplitbar.removeClass('active');
            } else {
                vsplitbar.addClass('active');
            }
            $.wiki.state.perspectives.ScanGalleryPerspective.width = x;
            sidebar[0].style.width = x + 'px';
        };

        /* The save button */
        $('#save-button').click(function(event){
            event.preventDefault();
            $.wiki.showDialog('#save_dialog');
        });

        $('.editor').hide();

        /*
         * TABS
         */
        $(document).on('click', '.tabs li', function(event, callback) {
            event.preventDefault();
            $.wiki.switchToTab(this);
        });

        $(document).on('click', '#tabs li .tabclose', function(event, callback) {
            var $tab = $(this).parent().parent();

            if($('a', $tab).is('.active'))
                $.wiki.switchToTab(DEFAULT_PERSPECTIVE);

            var p = $.wiki.perspectiveForTab($tab);
            p.destroy();

            return false;
        });

        $(window).resize(function(){
            splitterWidth = splitter.width();
        });

        $(window).resize();
        $.wiki.perspectiveForTab($('#tabs-right .active').parent()).onEnter();

        vsplitbar.on('click', function() {
            var $this = $(this);
            if ($this.hasClass('active')) {
                $.wiki.state.perspectives.ScanGalleryPerspective.lastWidth = sidebar.width();
                setSidebarWidth(0);
            } else {
                setSidebarWidth($.wiki.state.perspectives.ScanGalleryPerspective.lastWidth);
            }
        });

        /* Splitbar dragging support */
        vsplitbar
            .mousedown(function(e) {
                e.preventDefault();
                isHolding = true;
                if (sidebar.width() > MIN_SIDEBAR_WIDTH) {
                    $.wiki.state.perspectives.ScanGalleryPerspective.lastWidth = sidebar.width();
                }
            })
            .mousemove(function(e) {
                if(isHolding) {
                    dragLayer.show(); // We don't show it up until now so that we don't lose single click events on vsplitbar
                }
            });
        dragLayer.mousemove(function(e) {
            setSidebarWidth(splitterWidth - e.clientX - vsplitbarWidth / 2);
        });
        $('body').mouseup(function(e) {
            dragLayer.hide();
            isHolding = false;
        });

        setSidebarWidth($.wiki.state.perspectives.ScanGalleryPerspective.width);

        window.onbeforeunload = function(e) {
            if($.wiki.isDirty()) {
                e.returnValue = "Na stronie mogą być nie zapisane zmiany.";
                return "Na stronie mogą być nie zapisane zmiany.";
            };
        };

        $('body').mousemove(function(e) {
            CurrentDocument.active = new Date();
        });
        $('body').keydown(function(e) {
            CurrentDocument.active = new Date();
        });

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

                /* check for a newer version */
                CurrentDocument.checkRevision({outdated: function(){
                    $('#header').addClass('out-of-date');
                }});
                var revTimer = setInterval(function() {
                    CurrentDocument.checkRevision({outdated: function(){
                        $('#header').addClass('out-of-date');
                    }});
                }, 5 * 1000);
            },
            failure: function() {
                $('#loading-overlay').fadeOut();
                alert("FAILURE");
            }
        });
    }; /* end of initialize() */


    /* Load configuration */
    $.wiki.loadConfig();

    /*
     * Initialize all perspectives
     */
    $('.tabs li').each((i, e) => {
        $.wiki.initTab({tab: e, doc: CurrentDocument});
    });
    initialize();
});
