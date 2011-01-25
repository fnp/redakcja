/*
 *
 * XSLT STUFF
 *
 */
function createXSLT(xsl) {
    var p = new XSLTProcessor();
    p.importStylesheet(xsl);
    return p;
}

var xml2htmlStylesheet = null;

// Wykonuje block z załadowanymi arkuszami stylów
function withStylesheets(code_block, onError)
{
    if (!xml2htmlStylesheet) {
    	$.blockUI({message: 'Ładowanie arkuszy stylów...'});
    	$.ajax({
        	url: STATIC_URL + 'xsl/wl2html_client.xsl?20110112',
        	dataType: 'xml',
        	timeout: 10000,
        	success: function(data) {
            	xml2htmlStylesheet = createXSLT(data);
                $.unblockUI();
				code_block();

            },
			error: onError
        })
    }
	else {
		code_block();
	}
}


// Wykonuje block z załadowanymi kanonicznymi motywami
function withThemes(code_block, onError)
{
    if (typeof withThemes.canon == 'undefined') {
        $.ajax({
            url: '/themes',
            dataType: 'text',
            success: function(data) {
                withThemes.canon = data.split('\n');
                code_block(withThemes.canon);
            },
            error: function() {
                withThemes.canon = null;
                code_block(withThemes.canon);
            }
        })
    }
    else {
        code_block(withThemes.canon);
    }
}


function xml2html(options) {
    withStylesheets(function() {
        var xml = options.xml.replace(/\/(\s+)/g, '<br />$1');
        xml = xml.replace(/([^a-zA-Z0-9ąćęłńóśźżĄĆĘŁŃÓŚŹŻ\s<>«»\\*_!,:;?%."'=#()\/-]+)/g, '<alien>$1</alien>');
        var parser = new DOMParser();
        var serializer = new XMLSerializer();
        var doc = parser.parseFromString(xml, 'text/xml');
        var error = $('parsererror', doc);

        if (error.length == 0) {
            doc = xml2htmlStylesheet.transformToFragment(doc, document);
            console.log(doc.firstChild);

        if(doc.firstChild === null) {
            options.error("Błąd w przetwarzaniu XML.");
                return;
            }

            error = $('parsererror', doc);
        }

        if (error.length > 0 && options.error) {
            source = $('sourcetext', doc);
            source_text = source.text();
            source.text('');
            options.error(error.text(), source_text);
        } else {
            options.success(doc.firstChild);

            withThemes(function(canonThemes) {
                if (canonThemes != null) {
                    $('.theme-text-list').addClass('canon').each(function(){
                        var themes = $(this).html().split(',');
                        for (i in themes) {
                            themes[i] = $.trim(themes[i]);
                            if (canonThemes.indexOf(themes[i]) == -1)
                                themes[i] = '<span x-pass-thru="true" class="noncanon">' + themes[i] + "</span>"
                        }
                        $(this).html(themes.join(', '));
                    });
                }
            });
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
const NS_END = 3;

const NAMESPACES = {
	// namespaces not listed here will be assigned random names
	"http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf",
	"http://purl.org/dc/elements/1.1/": "dc",
	"http://www.w3.org/XML/1998/namespace": "xml"
};

function HTMLSerializer() {
	// empty constructor
}



HTMLSerializer.prototype._prepare = function() {
	this.stack = [];

	// XML namespace is implicit
	this.nsMap = {"http://www.w3.org/XML/1998/namespace": "xml"};

	this.result = "";
	this.nsCounter = 1;
}

HTMLSerializer.prototype._pushElement = function(element) {
	this.stack.push({
		"type": ELEM_START,
		"node": element
	});
}

HTMLSerializer.prototype._pushChildren = function(element) {
	for(var i = element.childNodes.length-1; i >= 0; i--)
		this._pushElement(element.childNodes.item(i));
}

HTMLSerializer.prototype._pushTagEnd = function(tagName) {
	this.stack.push({
		"type": ELEM_END,
		"tagName": tagName
	});
}

HTMLSerializer.prototype._verseBefore = function(node) {
    /* true if previous element is a previous verse of a stanza */
    var parent = node.parentNode;
    if (!parent || !parent.hasAttribute('x-node') || parent.getAttribute('x-node') != 'strofa')
        return false;

	var prev = node.previousSibling;

	while((prev !== null) && (prev.nodeType != ELEMENT_NODE)) {
		prev = prev.previousSibling;
	}

	return (prev !== null) && prev.hasAttribute('x-verse');
}

HTMLSerializer.prototype._nodeIgnored = function(node) {
    return node.getAttribute('x-node') == 'wers';
}

HTMLSerializer.prototype._ignoredWithWhitespace = function(node) {
    while (node.nodeType == ELEMENT_NODE && this._nodeIgnored(node) && node.childNodes.length > 0)
        node = node.childNodes[0];
    if (node.nodeType == TEXT_NODE)
        return node.nodeValue.match(/^\s/)
    else return false;
}


HTMLSerializer.prototype.serialize = function(rootElement, stripOuter)
{
	var self = this;
	self._prepare();

	if(!stripOuter)
		self._pushElement(rootElement);
	else
		self._pushChildren(rootElement);

    var text_buffer = '';

	while(self.stack.length > 0) {
		var token = self.stack.pop();

        if(token.type === ELEM_END) {
            self.result += text_buffer;
            text_buffer = '';
            if (token.tagName != '')
                self.result += "</" + token.tagName + ">";
            continue;
        };

		if(token.type === NS_END) {
			self._unassignNamespace(token.namespace);
			continue;
		}


		switch(token.node.nodeType) {
			case ELEMENT_NODE:
				if(token.node.hasAttribute('x-pass-thru')
				 || token.node.hasAttribute('data-pass-thru')) {
					self._pushChildren(token.node);
					break;
				}

				if(!token.node.hasAttribute('x-node'))
					break;

				var xnode = token.node.getAttribute('x-node');

				if(xnode === 'out-of-flow-text') {
					self._pushChildren(token.node);
					break;
				}

                if(token.node.hasAttribute('x-verse') && self._verseBefore(token.node)) {
                    self.result += '/';
                    // add whitespace if there's none
                    if (!(text_buffer.match(/^\s/) || self._ignoredWithWhitespace(token.node)))
                        self.result += ' ';
                }

                self.result += text_buffer;
                text_buffer = '';
				self._serializeElement(token.node);
				break;
			case TEXT_NODE:
				self.result += text_buffer;
				text_buffer = token.node.nodeValue;
				break;
		};
	};
    self.result += text_buffer;

	return this.result;
}

/*
 * TODO: this doesn't support prefix redefinitions
 */
HTMLSerializer.prototype._unassignNamespace = function(nsData) {
	this.nsMap[nsData.uri] = undefined;
};

HTMLSerializer.prototype._assignNamespace = function(uri) {
	if(uri === null) {
		// default namespace
		return ({"prefix": "", "uri": "", "fresh": false});
	}

	if(this.nsMap[uri] === undefined) {
		// this prefix hasn't been defined yet in current context
		var prefix = NAMESPACES[uri];

		if (prefix === undefined) { // not predefined
			prefix = "ns" + this.nsCounter;
			this.nsCounter += 1;
		}

		this.nsMap[uri] = prefix;
		return ({
			"prefix": prefix,
			"uri": uri,
			"fresh": true
		});
	}

	return ({"prefix": this.nsMap[uri], "uri": uri, "fresh": false});
};

HTMLSerializer.prototype._join = function(prefix, name) {
	if(!!prefix)
		return prefix + ":" + name;
	return name;
};

HTMLSerializer.prototype._rjoin = function(prefix, name) {
	if(!!name)
		return prefix + ":" + name;
	return prefix;
};

HTMLSerializer.prototype._serializeElement = function(node) {
    var self = this;

    if (self._nodeIgnored(node)) {
        self._pushTagEnd('');
        self._pushChildren(node);
    }
    else {
    	var ns = node.getAttribute('x-ns');
    	var nsPrefix = null;
    	var newNamespaces = [];

    	var nsData = self._assignNamespace(node.getAttribute('x-ns'));

    	if(nsData.fresh) {
    		newNamespaces.push(nsData);
    		self.stack.push({
    			"type": NS_END,
    			"namespace": nsData
    		});
    	}

    	var tagName = self._join(nsData.prefix, node.getAttribute('x-node'));

    	/* retrieve attributes */
    	var attributeIDs = [];
    	for (var i = 0; i < node.attributes.length; i++) {
    		var attr = node.attributes.item(i);

    		// check if name starts with "x-attr-name"
    		var m = attr.name.match(XATTR_RE);
    		if (m !== null)
    			attributeIDs.push(m[1]);
    	};

    	/* print out */

    	self.result += '<' + tagName;

    	$.each(attributeIDs, function() {
    		var nsData = self._assignNamespace(node.getAttribute('x-attr-ns-'+this));

    		if(nsData.fresh) {
    			newNamespaces.push(nsData);
    			self.stack.push({
    				"type": NS_END,
    				"namespace": nsData
    			});
    		};

    		self.result += ' ' + self._join(nsData.prefix, node.getAttribute('x-attr-name-'+this));
    		self.result += '="'+node.getAttribute('x-attr-value-'+this) +'"';
    	});

    	/* print new namespace declarations */
    	$.each(newNamespaces, function() {
    		self.result += " " + self._rjoin("xmlns", this.prefix);
    		self.result += '="' + this.uri + '"';
    	});

    	if (node.childNodes.length > 0) {
    		self.result += ">";
    		self._pushTagEnd(tagName);
    		self._pushChildren(node);
    	}
    	else {
    		self.result += "/>";
    	};
    }
};

function html2text(params) {
	try {
		var s = new HTMLSerializer();
		params.success( s.serialize(params.element, params.stripOuter) );
	} catch(e) {
		params.error("Nie udało się zserializować tekstu:" + e)
	}
}
