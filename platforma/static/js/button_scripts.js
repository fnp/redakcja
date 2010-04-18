(function() {
  var slice = Array.prototype.slice;

  function update(array, args) {
    var arrayLength = array.length, length = args.length;
    while (length--) array[arrayLength + length] = args[length];
    return array;
  };

  function merge(array, args) {
    array = slice.call(array, 0);
    return update(array, args);
  };

  Function.prototype.bind = function(context) {
    if (arguments.length < 2 && typeof arguments[0] === 'undefined') {
      return this;
    }
    var __method = this;
    var args = slice.call(arguments, 1);
    return function() {
      var a = merge(args, arguments);
      return __method.apply(context, a);
    }
  }

})();

function nblck_each(array, body, after) {
	$.each(array, function(i) {
		body(this, i);
	});

	after();
};

function nblck_map(array, func, after) {
	var acc = [];

	nblck_each(array, function(elem, index) {
		acc.push(func(elem, index));
	}, function(){
		after(acc);
	});
};

function ScriptletCenter()
{
    this.scriptlets = {};

    this.scriptlets['insert_tag'] = function(context, params, done)
    {
        var text = this.XMLEditorSelectedText(context);
        var start_tag = '<'+params.tag;
        var move_cursor = false;

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
            if(params.nocontent) {
                output = "<"+params.tag +" />";
            }
            else {
                output = start_tag + end_tag;
                move_cursor = true;
            }
        }

        this.XMLEditorReplaceSelectedText(context, output);

        try {
            if (move_cursor) {
                this.XMLEditorMoveCursorForward(context, params.tag.length+2);
            }
        } catch(e) {}

		done();
    }.bind(this);

    this.scriptlets['lineregexp'] = function(context, params, done) {
		var self = this;

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
        if(!text) return done();

        var changed = 0;
        var lines = text.split('\n');

		nblck_map(lines, function(line, index) {
            var old_line = line;
            $(exprs).each(function() {
                var expr = this;
                line = line.replace(expr.rx, expr.repl);
            });

			$progress.html(index);

            if(old_line != line) changed += 1;
            return line;
        }, function(newlines) {
			if(changed > 0) {
				self.XMLEditorReplaceSelectedText(context, newlines.join('\n') );
			};

			done();
		});
    }.bind(this);

    this.scriptlets['fulltextregexp'] = function(context, params, done) {
		var self = this;

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
        if(!text) return done();
        var original = text;

		nblck_each(exprs, function(expr, index) {
			$progress.html(600 + index);
            text = text.replace(expr.rx, expr.repl);
        }, function() {
			if( original != text) {
         	   self.XMLEditorReplaceSelectedText(context, text);
        	}

			done();
		});
    }.bind(this);

    this.scriptlets['macro'] = function(context, params, done) {
        var self = this;
		var i = 0;

		function next() {
        	if (i < params.length) {
				var e = params[i];
				i = i + 1;
				self.scriptlets[e[0]](context, e[1], next);
			}
			else {
				done();
			}
        };

		next();
    }.bind(this);

    this.scriptlets['lowercase'] = function(context, params, done)
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

		done();
    }.bind(this);


    this.scriptlets["insert_stanza"] = function(context, params, done) {
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

		done();
    }.bind(this);

}

ScriptletCenter.prototype.callInteractive = function(opts) {
	$progress = $('<span>Executing script</span>');
	var self = this;

	$.blockUI({
		message: $progress,

	});


	self.scriptlets[opts.action](opts.context, opts.extra, function(){
		$.unblockUI(); // done
	});
}

ScriptletCenter.prototype.XMLEditorSelectedText = function(editor) {

    return editor.selection();
};

ScriptletCenter.prototype.XMLEditorReplaceSelectedText = function(editor, replacement)
{
	$progress.html("Replacing text");
    editor.replaceSelection(replacement);
};

ScriptletCenter.prototype.XMLEditorMoveCursorForward = function(panel, n) {
    var pos = panel.cursorPosition();
    panel.selectLines(pos.line, pos.character + n);
};

var scriptletCenter;

$(function() {
    scriptletCenter = new ScriptletCenter();
});