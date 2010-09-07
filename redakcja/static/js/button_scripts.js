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

    this.scriptlets['insert_tag'] = function(context, params, text, move_forward, done)
    {
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

        if (move_cursor) {
            move_forward -= params.tag.length+3;
        }

        done(output, move_forward);
    }.bind(this);

    this.scriptlets['lineregexp'] = function(context, params, text, move_forward, done) {
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
        if(!text) done(text, move_forward);

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
                text = newlines.join('\n');
            };

            done(text, move_forward);
		});
    }.bind(this);

    this.scriptlets['fulltextregexp'] = function(context, params, text, move_forward, done) {
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

        if(!text) done(text, move_forward);
        var original = text;$

		nblck_each(exprs, function(expr, index) {
			$progress.html(600 + index);
            text = text.replace(expr.rx, expr.repl);
        }, function() {
			done(text, move_forward);
		});
    }.bind(this);

    this.scriptlets['macro'] = function(context, params, text, move_forward, done) {
        var self = this;
		var i = 0;

		function next(text, move_forward) {
        	if (i < params.length) {
				var e = params[i];
				i = i + 1;
				self.scriptlets[e[0]](context, e[1], text, move_forward, next);
			}
			else {
				done(text, move_forward);
			}
        };

		next(text, move_forward);
    }.bind(this);

    this.scriptlets['lowercase'] = function(context, params, text, move_forward, done)
    {
        if(!text) done(text, move_forward);
        done(text.toLowerCase(), move_forward);
    }.bind(this);


    this.scriptlets["insert_stanza"] = function(context, params, text, move_forward, done) {
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
        }
        else {
            text = "<strofa></strofa>"
            move_forward -= "</strofa>".length;
        }

        done(text, move_forward);
    }.bind(this);

}

ScriptletCenter.prototype.callInteractive = function(opts) {
	$progress = $('<span>Executing script</span>');
	var self = this;

	/* This won't work, 'cause the JS below might be synchronous :( */
	/* var timer = setTimeout(function() {
	    $.blockUI({message: $progress});
	    timer = null;
	}, 1000); */

	$.blockUI({message: $progress, showOverlay: false});

    var input = self.XMLEditorSelectedText(opts.context);
	self.scriptlets[opts.action](opts.context, opts.extra, input, 0, function(output, move_forward){
	    /*if(timer)
	        clearTimeout(timer);
	    else */
        if (input != output) {
            self.XMLEditorReplaceSelectedText(opts.context, output)
        }
        if (move_forward) {
            try {
                self.XMLEditorMoveCursorForward(opts.context, move_forward)
            }
            catch(e) {}
        }
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