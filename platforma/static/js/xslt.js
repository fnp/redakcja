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
    
    // Mozilla nie uważa deklaracji namespace za atrybuty | --lqc: bo nie są one atrybutami!
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
            doc = xml2htmlStylesheet.transformToDocument(doc);
			console.log(doc);
            error = $('parsererror', doc);
        }
        
        if (error.length > 0 && options.error) {
            options.error(error.text());
        } else {			
            options.success(document.importNode(doc.documentElement, true));
        }
    }, function() { options.error && options.error('Nie udało się załadować XSLT'); });
}

/* USEFULL CONSTANTS */
const ELEMENT_NODE 					 = 1;
const ATTRIBUTE_NODE                 = 2;
const TEXT_NODE                      = 3;
const CDATA_SECTION_NODE             = 4;
const ENTITY_REFERENCE_NODE          = 5;
const ENTITY_NODE                    = 6;
const PROCESSING_INSTRUCTION_NODE    = 7;
const COMMENT_NODE                   = 8;
const DOCUMENT_NODE                  = 9;
const DOCUMENT_TYPE_NODE             = 10;
const DOCUMENT_FRAGMENT_NODE         = 11;
const NOTATION_NODE                  = 12;
const XATTR_RE = /^x-attr-name-(.*)$/;

const ELEM_START = 1;
const ELEM_END = 2;

const NAMESPACES = {
	undefined: "",
	null: "",	
	"": "",
	"http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf:",
	"http://purl.org/dc/elements/1.1/": "dc:",
	"http://www.w3.org/XML/1998/namespace": "xml:"
};

function html2text(rootElement) {
	var stack = [];
	var result = "";
	
	stack.push([ELEM_START, rootElement]);	
	console.log("SERIALIZING")
	
	while( stack.length > 0) {
		var pair = stack.pop();
		
		var event = pair[0];
		var node = pair[1];
		
		// console.log("NODE", event, node);
		
		if(event == ELEM_END) {
			result += "</" + node + ">\n";
			continue;
		};
		
		switch(node.nodeType) {
			case ELEMENT_NODE:
				if(!node.hasAttribute('x-node'))
					break;
					
				var tag_name = NAMESPACES[node.getAttribute('x-ns')] + node.getAttribute('x-node');
				// console.log("ELEMENT: ", tag_name);
				
				/* retrieve attributes */
				var attr_ids = [];
				for(var i=0; i < node.attributes.length; i++) {
					var attr = node.attributes.item(i);
					
					// check if name starts with "x-attr-name"
					var m = attr.name.match(XATTR_RE);
					if(m !== null) 
						attr_ids.push(m[1]);						
					
				};
				
				result += '<' + tag_name;
				
				$.each(attr_ids, function() {										
					result += ' ' + NAMESPACES[node.getAttribute('x-attr-ns-'+this)];
					result += node.getAttribute('x-attr-name-'+this);
					result += '="'+node.getAttribute('x-attr-value-'+this) +'"';
				});								
				result += '>'
				
				stack.push([ELEM_END, tag_name]);
				for(var i = node.childNodes.length-1; i >= 0; i--)
					stack.push([ELEM_START, node.childNodes.item(i)]);				
				
				break;			
			case TEXT_NODE:
				result += node.nodeValue;
				break;
		}		
	}
	
	return result;
}

function html2xml(options) {
	try {
		return options.success(html2text(options.htmlElement));
	} catch(e) {
		options.error("Nie udało się zserializować tekstu:" + e)
	}    
};