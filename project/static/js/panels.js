$(function() {
    // ========================
    // = Resizable panels =
    // ========================
    function resizePanels() {
        $('.panel').height($(window).height() - $('.panel').position().top);
        $('#right-panel-wrap').width($(window).width() - $('#left-panel-wrap').outerWidth());
    }
    
    $(window).resize(function() {
        resizePanels();
    })
    
    $('#left-panel-wrap').bind('resizable:resize', resizePanels)
        .resizable('#slider', {minWidth: 8});
    
    resizePanels();
    
    $('.panel-toolbar select').change(function() {
        console.log('loading panel', $(this).val(), 'into', $('.panel-contents', $(this).parent()));
    });
    // $('#id_folders').change(function() {
    //     $('#images').load('{% url folder_image_ajax %}' + $('#id_folders').val() + '/', function() {
    //         $('#images-wrap').data('lazyload:lastCheckedScrollTop', -10000);
    //     });
    // });
    // 
    //
    
    // var editor = CodeMirror.fromTextArea("id_text", {
    //     parserfile: 'parsexml.js',
    //     path: "/static/js/codemirror/",
    //     stylesheet: "/static/css/xmlcolors.css",
    //     parserConfig: {useHTMLKludges: false},
    //     initCallback: function() {
    //         $('#images').autoscroll('iframe');
    //         $('.toggleAutoscroll').toggle(function() {
    //             $(this).html('Synchronizuj przewijanie');
    //             $('#images').disableAutoscroll();
    //         }, function() {
    //             $(this).html('Nie synchronizuj przewijania');
    //             $('#images').enableAutoscroll();
    //         })
    //         
    //         // Toolbar
    //         $('#toolbar-tabs li').click(function() {
    //             var id = $(this).attr('p:button-list');
    //             $('#toolbar-tabs li').removeClass('active');
    //             $(this).addClass('active');
    //             if (!$('#' + id).is(':visible')) {
    //                 $('#toolbar-buttons ol').not('#' + id).hide();
    //                 $('#' + id).show();
    //             }
    //         })
    // 
    //         var keys = {};
    //         $('#toolbar-buttons li').each(function() {
    //             var tag = $(this).attr('p:tag');
    //             var handler = function() {
    //                 var text = editor.selection();
    //                 editor.replaceSelection('<' + tag + '>' + text + '</' + tag + '>');
    //                 if (text.length == 0) {
    //                     var pos = editor.cursorPosition();
    //                     editor.selectLines(pos.line, pos.character + tag.length + 2);
    //                 }
    //             }
    //             if ($(this).attr('p:key')) {
    //                 keys[$(this).attr('p:key')] = handler;
    //             }
    //             $(this).click(handler)
    //         });
    //         
    //         editor.grabKeys(function(event) { 
    //             if (keys[event.keyCode]) {
    //                 keys[event.keyCode]();
    //             }
    //         }, function(event) {
    //             return event.altKey && keys[event.keyCode];
    //         });
    //     }
    // });
    

    

    
    // $('#toolbar-buttons li').wTooltip({
    //     delay: 1000, 
    //     style: {
    //         border: "1px solid #7F7D67",
    //         opacity: 0.9, 
    //         background: "#FBFBC6", 
    //         padding: "1px",
    //         fontSize: "12px",
    //     }});
    
    // $('#images-wrap').lazyload('.image-box', {threshold: 640 * 10, scrollTreshold: 640 * 5});
});
