function serialize(element) {
    if (element.nodeType == 3) { // tekst
        return [$.trim(element.nodeValue)];
    } else if (element.nodeType != 1) { // pomijamy węzły nie będące elementami XML ani tekstem
        return [];
    }
    
    var result = [];
    var hasContent = false;
    
    result.push('<');
    result.push(element.tagName);
    
    // Mozilla nie uważa deklaracji namespace za atrybuty
    var ns = element.tagName.indexOf(':');
    if (ns != -1 && $.browser.mozilla) {
        result.push(' xmlns:');
        result.push(element.tagName.substring(0, ns));
        result.push('="');
        result.push(element.namespaceURI);
        result.push('"');
    }
    
    if (element.attributes) {
        for (var i=0; i < element.attributes.length; i++) {
            var attr = element.attributes[i];
            result.push(' ');
            result.push(attr.name);
            result.push('="');
            result.push(attr.value);
            result.push('"');
            hasContent = true;
        }
    }
    
    if (element.childNodes.length == 0) {
        result.push(' />');
    } else {
        result.push('>');

        for (var i=0; i < element.childNodes.length; i++) {
            result = result.concat(serialize(element.childNodes[i]));
        }

        result.push('</');
        result.push(element.tagName);
        result.push('>');
    }
    
    if (element.tagName == 'akap' || element.tagName == 'akap_dialog' || element.tagName == 'akap_cd') {
        result.push('\n\n\n');
    } else if (element.tagName == 'rdf:RDF') {
        result.push('\n\n\n\n\n');
    } else if (element.tagName.indexOf('dc:') != -1) {
        result.push('\n');
    }
    
    return result;
};


$(function() {
    var editor = CodeMirror.fromTextArea('id_text', {
        parserfile: 'parsexml.js',
        path: "/static/js/lib/codemirror/",
        stylesheet: "/static/css/xmlcolors.css",
        parserConfig: {
            useHTMLKludges: false
        },
        textWrapping: true,
        tabMode: 'spaces',
        indentUnit: 0,
    });
    
    $('#splitter').splitter({
        type: "v",
        outline: true,
        minLeft: 480,
        sizeRight: 0,
        anchorToWindow: true,
        resizeToWidth: true,
    });
    
    $(window).resize(function() {
        $('iframe').height($(window).height() - $('#tabs').outerHeight());
    });
    
    $(window).resize();
    
    $('.vsplitbar').dblclick(function() {
        if ($('#sidebar').width() == 0) {
            $('#splitter').trigger('resize', [$(window).width() - 480]);
        } else {
            $('#splitter').trigger('resize', [$(window).width()]);
        }
    });

    loadSuccess = function() {
        if (this.get('state') != 'loading') {
            alert('erroneous state:', this.get('state'));
        }
    }
                
    function createXSLT(xsl) {
        var p = new XSLTProcessor();
        p.importStylesheet(xsl);
        return p;
    }
    
    function transform() {
        $.ajax({
            url: '/static/xsl/wl2html_client.xsl',
            dataType: 'xml',
            success: function(data) {
                var doc = null;
                var parser = new DOMParser();
                var serializer = new XMLSerializer();
                var htmlXSL = createXSLT(data);
                
                doc = editor.getCode().replace(/\/\s+/g, '<br />');
                doc = parser.parseFromString(doc, 'text/xml');
                console.log('xml', doc);
                doc = htmlXSL.transformToFragment(doc, document);
                console.log('after transform', doc);
                $('#html-view').html(doc.firstChild);
            },
            error: function() {alert('Error loading XSL!')}
        });        
    };
    
    function reverseTransform () {
        $.ajax({
            url: '/static/xsl/html2wl_client.xsl',
            dataType: 'xml',
            success: function(data) {
                var doc = null;
                var parser = new DOMParser();
                var serializer = new XMLSerializer();
                var xsl = createXSLT(data);
                
                doc = serializer.serializeToString($('#html-view div').get(0))
                doc = parser.parseFromString(doc, 'text/xml');
                console.log('xml',doc, doc.documentElement);
                // TODO: Sprawdzenie błędów
                doc = xsl.transformToDocument(doc);
                console.log('after transform', doc, doc.documentElement);
                doc = serialize(doc.documentElement).join('');
                // doc = serializer.serializeToString(doc.documentElement)
                editor.setCode(doc);
            },
            error: function() {alert('Error loading XSL!')}
        });
    };
    
    $('#save-button').click(function(event) {
        event.preventDefault();
        console.log(editor.getCode(), $('form input[name=text]').get(0));
        $('form textarea[name=text]').val(editor.getCode());
        $('form').ajaxSubmit(function() {
            alert('Udało się!');
        });
    });
    
    $('#simple-view-tab').click(function() {
        if ($(this).hasClass('active')) {
            return;
        }
        $(this).addClass('active');
        $('#source-view-tab').removeClass('active');
        $('#source-editor').hide();
        $('#simple-editor').show();
        transform();
    });
    
    $('#source-view-tab').click(function() {
        if ($(this).hasClass('active')) {
            return;
        }
        $(this).addClass('active');
        $('#simple-view-tab').removeClass('active');
        $('#simple-editor').hide();
        $('#source-editor').show();
        reverseTransform();
    });
    
    $('.toolbar button').click(function(event) {
        event.preventDefault();
        var params = eval("(" + $(this).attr('ui:action-params') + ")");
        scriptletCenter.scriptlets[$(this).attr('ui:action')](editor, params);
    });
    
    $('.toolbar select').change(function() {
        var slug = $(this).val();
        
        $('.toolbar-buttons-container').hide().filter('[data-group=' + slug + ']').show();
    });
    
    $('.toolbar-buttons-container').hide();
    $('.toolbar select').change();
    
    // $('#html-view *[x-editable]').live('mouseover', function() {
    //     $(this).css({backgroundColor: 'red', marginLeft: -50, paddingLeft: 50});
    //     $(this).append('<button class="edit-button">Edytuj</button>');
    // }).live('mouseout', function() {
    //     $(this).css({backgroundColor: null, marginLeft: 0, paddingLeft: 0});
    //     $('.edit-button', this).remove();
    // });
});
