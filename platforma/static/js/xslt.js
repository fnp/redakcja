var MARGIN = {
    dramat_wierszowany_l: 4,
    dramat_wierszowany_lp: 4,
    dramat_wspolczesny: 4,
    wywiad: 4,
    opowiadanie: 4,
    powiesc: 4,
    liryka_l: 4,
    liryka_lp: 4,
    naglowek_czesc: 4,
    naglowek_akt: 4,
    naglowek_rozdzial: 4,
    naglowek_osoba: 4,
    lista_osob: 4,
    
    akap: 3,
    akap_cd: 3,
    akap_dialog: 3,
    strofa: 3,
    motto: 3, 
    miejsce_czas: 3,
        
    autor_utworu: 2,
    nazwa_utworu: 2,
    dzielo_nadrzedne: 2,
    didaskalia: 2,
    motto_podpis: 2,
    naglowek_listy: 2,
    
    kwestia: 1,
    lista_osoba: 1
}

MARGIN['rdf:RDF'] = 3;
MARGIN['rdf:Description'] = 2;

var blockTags = ['akap', 'akap_cd', 'akap_dialog', 'strofa', 'didaskalia', 'wers', 'wers_cd', 'wers_akap', 'wers_wciety', 'autor_utworu', 'nazwa_utworu', 'dzielo_nadrzedne', 'podpis'];
function elementType(element) {
    if (blockTags.indexOf(element.tagName) != -1) {
        return 'inline';
    } else {
        return 'block';
    }
}

// Serializuje XML, wstawiając odpowiednie ilości białych znaków między elementami
function serialize(element, mode) {
    if (!mode) {
        mode = 'block';
    }
    
    if (element.nodeType == 3) { // tekst
    	return [element.nodeValue];        
    } else if (element.nodeType != 1) { // pomijamy węzły nie będące elementami XML ani tekstem
        return [];
    }
    
    var result = [];
    var hasContent = false;
    
    
    
    if (MARGIN[element.tagName]) {
        for (var i=0; i < MARGIN[element.tagName]; i++) {
            result.push('\n');
        };
    } else if (element.tagName.indexOf('dc:') != -1) {
        result.push('\n');
    }
    
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
            result = result.concat(serialize(element.childNodes[i], 
                mode == 'inline' ? 'inline' : elementType(element.childNodes[i])));
        }

        result.push('</');
        result.push(element.tagName);
        result.push('>');
    }
    
    return result;
};


function createXSLT(xsl) {
    var p = new XSLTProcessor();
    p.importStylesheet(xsl);
    return p;
}


var xml2htmlStylesheet = null;
var html2xmlStylesheet = null;


// Wykonuje block z załadowanymi arkuszami stylów
function withStylesheets(block, onError) {
    if (xml2htmlStylesheet && html2xmlStylesheet) {
        block();
        return;
    }
    $.blockUI({message: 'Ładowanie arkuszy stylów...'});
    $.ajax({
        url: STATIC_URL + 'xsl/wl2html_client.xsl',
        dataType: 'xml',
        success: function(data) {
            xml2htmlStylesheet = createXSLT(data);
            $.ajax({
                url: STATIC_URL + 'xsl/html2wl_client.xsl',
                dataType: 'xml',
                success: function(data) {
                    html2xmlStylesheet = createXSLT(data);
                    $.unblockUI();
                    block();
                },
                error: onError
            })
        },
        error: onError
    })
}


function xml2html(options) {
    withStylesheets(function() {
        var xml = options.xml.replace(/\/\s+/g, '<br />');
        var parser = new DOMParser();
        var serializer = new XMLSerializer();
        var doc = parser.parseFromString(xml, 'text/xml');
        var error = $('parsererror', doc);
        
        if (error.length == 0) {
            doc = xml2htmlStylesheet.transformToFragment(doc, document);
            error = $('parsererror', doc);
        }
        
        if (error.length > 0 && options.error) {
            options.error(error.text());
        } else {
            options.success(doc.firstChild);
        }
    }, function() { options.error && options.error('Nie udało się załadować XSLT'); });
}


function html2xml(options) {
    withStylesheets(function() {
        var xml = options.xml;
        var parser = new DOMParser();
        var serializer = new XMLSerializer();
        var doc = parser.parseFromString(xml, 'text/xml');
        var error = $('parsererror', doc.documentElement);

        if (error.length == 0) {
            doc = html2xmlStylesheet.transformToDocument(doc);
            error = $('parsererror', doc.documentElement);
        }
        
        if (error.length > 0 && options.error) {
            options.error(error.text());
        } else {
            if (options.inner) {
                var result = [];
                for (var i = 0; i < doc.documentElement.childNodes.length; i++) {
                    result.push(serialize(doc.documentElement.childNodes[i]).join(''));
                };
                options.success(result.join(''));
            } else {
                options.success(serialize(doc.documentElement).join(''));
            }
        }
    }, function() { options.error && options.error('Nie udało się załadować XSLT'); });
};
