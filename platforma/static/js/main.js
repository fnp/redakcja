if (!window.console) {
    window.console = {
        log: function() {}
    }
}

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
        $('img', element).attr('src', element.data('images')[pageNumber - 1]);
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
    
    
    var image = $('img', element).attr('unselectable', 'on');
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
        $('.gallery-image').animate({top: 53}, 200);
        $('.chosen-gallery').focus();
    });
    $('.change-gallery-ok', element).click(function() {
        if ($('#document-meta .gallery').length == 0) {
            $('<div class="gallery"></div>').appendTo('#document-meta');
        }
        $('#document-meta .gallery').html($('.chosen-gallery').val());
        updateGallery($('.chosen-gallery').val());
        $('.gallery-image').animate({top: 27}, 200);
    });
    $('.change-gallery-cancel', element).click(function() {
        $('.gallery-image').animate({top: 27}, 200);
    });
    
    $('img', element).load(function() {
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
            setTimeout(function() { $('img', element).load(); }, 100);
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
                $('img', element).show();
            },
            
            error: function(data) {
                element.data('images', []);
                pn.val(1);
                pn.change();
                $('img', element).hide();
            }
        });
    }
    
    if (url) {
        updateGallery(url);
    }
}


function transform(editor) {
    $.blockUI({message: 'Ładowanie...'});
    setTimeout(function() {
        xml2html({
            xml: editor.getCode(),
            success: function(element) {
                $('#html-view').html(element);
                $.unblockUI();
            }, error: function(text) {
                $('#html-view').html('<p class="error">Wystąpił błąd:</p><pre>' + text + '</pre>');
                $.unblockUI();
            }
        });
    }, 200);
};


function reverseTransform(editor, cont) {
    var serializer = new XMLSerializer();
    if ($('#html-view .error').length > 0) {
        return;
    }
    $.blockUI({message: 'Ładowanie...'});
    setTimeout(function() {
        html2xml({
            xml: serializer.serializeToString($('#html-view div').get(0)),
            success: function(text) {
                editor.setCode(text);
                $.unblockUI();
                if (cont) {
                    cont();
                }
            }, error: function(text) {
                $('#source-editor').html('<p>Wystąpił błąd:</p><pre>' + text + '</pre>');
                $.unblockUI();
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
    
    
    function openForEdit($origin)
    {       
        // if(this.currentOpen && this.currentOpen != $origin) {
        //     this.closeWithSave(this.currentOpen);
        // }
        
        var $box = null
    
        // annotations overlay their sub box - not their own box //
        if($origin.is(".annotation-inline-box")) {
            $box = $("*[x-annotation-box]", $origin);
            console.log('annotation!', $box);
        } else {
            $box = $origin;
        }
        
        var x = $box[0].offsetLeft;
        var y = $box[0].offsetTop;
        var w = $box.outerWidth();
        var h = $box.innerHeight();
    
        console.log('width:', w, 'height:', h);

        // start edition on this node
        var $overlay = $('<div class="html-editarea"><textarea></textarea></div>').css({
            position: 'absolute',
            height: h,
            left: x,
            top: y,
            width: w
            // right: 0
        }).appendTo($box[0].offsetParent || element).show();
        
        console.log($overlay, $box[0].offsetParent || element);
        
        var serializer = new XMLSerializer();
    
        console.log($box.html());
        html2xml({
            xml: serializer.serializeToString($box[0]),
            inner: true,
            success: function(text) {
                $('textarea', $overlay).val($.trim(text));
                console.log($.trim(text));
                
                setTimeout(function() {
                    $('textarea', $overlay).focus();
                }, 100);
                
                $('textarea', $overlay).one('blur', function(event) {
                    var nodeName = $box.attr('x-node') || 'pe';
                    xml2html({
                        xml: '<' + nodeName + '>' + $('textarea', $overlay).val() + '</' + nodeName + '>',
                        success: function(element) {
                            $box.html($(element).html());
                            $overlay.remove();
                        },
                        error: function(text) {
                            $overlay.remove();
                            alert('Błąd! ' + text);
                        }
                    })
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
    });

    $('.motyw').live('click', function() {
        selectTheme($(this).attr('theme-class'));
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
                        author: 'annonymous',
                        comment: $('#komentarz').val()
                    };

                    console.log(data);

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
                                console.log(data.errors);
                                alert(data.errors);
                            }
                            $.unblockUI();
                        },
                        error: function(xhr, textStatus, errorThrown) {
                            alert('error: ' + textStatus + ' ' + errorThrown);
                        },
                    })
                }
                
                if ('#simple-view-tab.active') {
                    reverseTransform(editor, doSave);
                } else {
                    doSave();
                }
            });
            
            $('#save-cancel').click(function() {
                $.unblockUI();
            });

            $('#simple-view-tab').click(function() {
                if ($(this).hasClass('active')) {
                    return;
                }
                $(this).addClass('active');
                $('#source-view-tab').removeClass('active');
                $('#source-editor').hide();
                $('#simple-editor').show();
                transform(editor);
            });

            $('#source-view-tab').click(function() {
                if ($(this).hasClass('active')) {
                    return;
                }
                $(this).addClass('active');
                $('#simple-view-tab').removeClass('active');
                $('#simple-editor').hide();
                $('#source-editor').show();
                reverseTransform(editor);
            });

            $('#source-editor .toolbar button').click(function(event) {
                event.preventDefault();
                var params = eval("(" + $(this).attr('ui:action-params') + ")");
                scriptletCenter.scriptlets[$(this).attr('ui:action')](editor, params);
            });

            $('.toolbar select').change(function() {
                var slug = $(this).val();

                $('.toolbar-buttons-container').hide().filter('[data-group=' + slug + ']').show();
                $(window).resize();
            });

            $('.toolbar-buttons-container').hide();
            $('.toolbar select').change();

            $('#simple-view-tab').click();
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
