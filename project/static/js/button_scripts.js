function ScriptletCenter()
{
    this.scriptlets = {};

    this.scriptlets['insert_tag'] = function(context, params)
    {
        var text = this.XMLEditorSelectedText(context);
        var start_tag = '<'+params.tag;

        for (var attr in params.attrs) {
            start_tag += ' '+attr+'="' + params.attrs[attr] + '"';
        }

        start_tag += '>';
        var end_tag = '</'+params.tag+'>';

        if(text.length > 0) {
            // tokenize
            var output = '';
            var token = '';
            for(var index=0; index < text.length; index++)
            {
                if (text[index].match(/\s/)) { // whitespace
                    token += text[index];
                }
                else { // character
                    output += token;
                    if(output == token) output += start_tag;
                    token = '';
                    output += text[index];
                }
            }

            if( output[output.length-1] == '\\' ) {
                output = output.substr(0, output.length-1) + end_tag + '\\';
            } else {
                output += end_tag;
            }
            output += token;
        }
        else {
            output = start_tag + end_tag;
        }

        if (text.length === 0) {
            this.XMLEditorMoveCursorForward(context, params.tag.length + 2);
        }

        this.XMLEditorReplaceSelectedText(context, output);
    }.bind(this);

    this.scriptlets['lineregexp'] = function(context, params) {

        var exprs = $.map(params.exprs, function(expr) {
            var opts = "g";
            if(expr.length > 2) {
                opts = expr[2];
            } return {
                rx: new RegExp(expr[0], opts),
                repl: expr[1]
                };
        });

        var partial = true;
        var text = this.XMLEditorSelectedText(context);
        if(!text) return;

        var changed = 0;
        var lines = text.split('\n');
        lines = $.map(lines, function(line) {
            var old_line = line;
            $(exprs).each(function() {
                var expr = this;
                line = line.replace(expr.rx, expr.repl);
            });

            if(old_line != line) changed += 1;
            return line;
        });

        if(changed > 0) {
            this.XMLEditorReplaceSelectedText(context, lines.join('\n') );
        }
    }.bind(this);

    this.scriptlets['codemirror_fontsize'] = function(context, params) {
        var frameBody = this.XMLEditorBody(context);

        if(params.fontSize) {
            frameBody.css('font-size', params.fontSize);
        }
        else {
            var old_size = parseInt(frameBody.css('font-size'), 10);
            frameBody.css('font-size', old_size + (params.change || 0) );
        }
        
    }.bind(this);

    this.scriptlets['fulltextregexp'] = function(context, params) {
        var exprs = $.map(params.exprs, function(expr) {
            var opts = "mg";
            if(expr.length > 2) {
                opts = expr[2];
            }
            return {
                rx: new RegExp(expr[0], opts),
                repl: expr[1]
                };
        });

        var text = this.XMLEditorSelectedText(context);
        if(!text) return;
        var original = text;
        $(exprs).each(function() {
            text = text.replace(this.rx, this.repl);
        });

        if( original != text) {
            this.XMLEditorReplaceSelectedText(context, text);
        }
    }.bind(this);

    this.scriptlets['macro'] = function(context, params) {
        var self = this;

        $(params).each(function() {
            $.log(this[0], this[1]);
            self.scriptlets[this[0]](context, this[1]);
        });
    }.bind(this);

    this.scriptlets['lowercase'] = function(context, params)
    {
        var text = this.XMLEditorSelectedText(context);

        if(!text) return;

        var repl = '';
        var lcase = text.toLowerCase();
        var ucase = text.toUpperCase();

        if(lcase == text) repl = ucase; /* was lowercase */
        else if(ucase != text) repl = lcase; /* neither lower- or upper-case */
        else { /* upper case -> camel-case */
            var words = $(lcase.split(/\s/)).map(function() {
                if(this.length > 0) { 
                    return this[0].toUpperCase() + this.slice(1);
                } else {
                    return '';
                }
            });
            repl = words.join(' ');
        }

        if(repl != text) this.XMLEditorReplaceSelectedText(context, repl);
    }.bind(this);


    this.scriptlets["insert_stanza"] = function(context, params) {
        var text = this.XMLEditorSelectedText(context);

        if(text) {
            var verses = text.split('\n');
            text = ''; var buf = ''; var ebuf = '';
            var first = true;

            for(var i=0;  i < verses.length; i++) {
                var verse = verses[i].replace(/^\s+/, "").replace(/\s+$/, "");
                if(verse) {
                    text += (buf ? buf + '/\n' : '') + ebuf;
                    buf = (first ? '<strofa>\n' : '') + verses[i];
                    ebuf = '';
                    first = false;
                } else {
                    ebuf += '\n' + verses[i];
                }
            }
            text = text + buf + '\n</strofa>' + ebuf;
            this.XMLEditorReplaceSelectedText(context, text);
        }

        if (!text) {
            this.XMLEditorMoveCursorForward(context, params.tag.length + 2);
        }
        
    }.bind(this);

}

ScriptletCenter.prototype.XMLEditorSelectedText = function(panel) {
    return panel.contentView.editor.selection();
};

ScriptletCenter.prototype.XMLEditorReplaceSelectedText = function(panel, replacement)
{
    panel.contentView.editor.replaceSelection(replacement);
    // Tell XML view that it's data has changed
    panel.contentView.editorDataChanged();
};

ScriptletCenter.prototype.XMLEditorMoveCursorForward = function(panel, n) {
    var pos = panel.contentView.editor.cursorPosition();
    panel.contentView.editor.selectLines(pos.line, pos.character + n);
};

var scriptletCenter;

$(function() {
    scriptletCenter = new ScriptletCenter();
});