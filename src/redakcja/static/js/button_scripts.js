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

    this.scriptlets['insert_text'] = function(context, params, text, move_forward, move_up, done)
    {
        done(params.text, move_forward, move_up);
    }.bind(this);

    this.scriptlets['insert_tag'] = function(context, params, text, move_forward, move_up, done)
    {
        var padding_top = '';
        for (var i=params.padding_top; i; i--)
            padding_top += '\n';

        var start_tag = '<'+params.tag;
        var cursor_inside = false;

        for (var attr in params.attrs) {
            start_tag += ' '+attr+'="' + params.attrs[attr] + '"';
        }

        start_tag += '>';
        var end_tag = '</'+params.tag+'>';

        var padding_bottom = '';
        for (var i=params.padding_bottom; i; i--)
            padding_bottom += '\n';

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
                    if(output == token) output += padding_top + start_tag;
                    token = '';
                    output += text[index];
                }
            }

            if( output[output.length-1] == '\\' ) {
                output = output.substr(0, output.length-1) + end_tag + padding_bottom + '\\';
            } else {
                output += end_tag + padding_bottom;
            }
            output += token;

            // keep cursor inside tag if some previous scriptlet has already moved it
            cursor_inside = move_forward != 0 || move_up != 0;
        }
        else {
            if(params.nocontent) {
                output = padding_top + "<"+params.tag +" />" + padding_bottom;
            }
            else {
                output = padding_top + start_tag + end_tag + padding_bottom;
                cursor_inside = true;
            }
        }

        if (cursor_inside) {
            move_forward -= params.tag.length + 3;
            move_up += params.padding_bottom || 0;
        }

        done(output, move_forward, move_up);
    }.bind(this);

    this.scriptlets['lineregexp'] = function(context, params, text, move_forward, move_up, done) {
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

        if(!text) done(text, move_forward, move_up);

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

            done(text, move_forward, move_up);
		});
    }.bind(this);

    this.scriptlets['fulltextregexp'] = function(context, params, text, move_forward, move_up, done) {
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

        if(!text) done(text, move_forward, move_up);

		nblck_each(exprs, function(expr, index) {
			$progress.html(600 + index);
            text = text.replace(expr.rx, expr.repl);
        }, function() {
			done(text, move_forward, move_up);
		});
    }.bind(this);

    this.scriptlets['macro'] = function(context, params, text, move_forward, move_up, done) {
        var self = this;
		var i = 0;

		function next(text, move_forward, move_up) {
        	if (i < params.length) {
				var e = params[i];
				i = i + 1;
				self.scriptlets[e[0]](context, e[1], text, move_forward, move_up, next);
			}
			else {
				done(text, move_forward, move_up);
			}
        };

		next(text, move_forward, move_up);
    }.bind(this);

    this.scriptlets['lowercase'] = function(context, params, text, move_forward, move_up, done)
    {
        if(!text) done(text, move_forward, move_up);
        done(text.toLowerCase(), move_forward, move_up);
    }.bind(this);


    this.scriptlets["insert_stanza"] = function(context, params, text, move_forward, move_up, done) {
        var padding_top = '';
        for (var i=params.padding_top; i; i--)
            padding_top += '\n';

        var padding_bottom = '';
        for (var i=params.padding_bottom; i; i--)
            padding_bottom += '\n';

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
            text = padding_top + text + buf + '\n</strofa>' + padding_bottom + ebuf;
        }
        else {
            text = padding_top + "<strofa></strofa>" + padding_bottom;
            move_forward -= "</strofa>".length;
            move_up += params.padding_bottom || 0;
        }

        done(text, move_forward, move_up);
    }.bind(this);


    this.scriptlets['autotag'] = function(context, params, text, move_forward, move_up, done)
    {
        if(!text.match(/^\n+$/)) done(text, move_forward, move_up);

        var output = '';

        function insert_done(text, mf, mu) {
            output += text;
        }

        if (!params.split) params.split = 2;
        if (!params.padding) params.padding = 3;

        if (params.tag == 'strofa')
            tagger = this.scriptlets['insert_stanza'];
        else
            tagger = this.scriptlets['insert_tag'];

        var padding_top = text.match(/^\n+/)
        output = padding_top ? padding_top[0] : '';

        padding = '';
        for(var i=params.padding; i; --i) {
            padding += "\n";
        }

        text = text.substr(output.length);
        var chunk_reg = new RegExp("^([\\s\\S]+?)(\\n{"+params.split+",}|$)");
        while (match = text.match(chunk_reg)) {
            if (params.tag == 'akap' && match[1].match(/^---/))
                tag = 'akap_dialog';
            else tag = params.tag;
            tagger(context, {tag: tag}, match[1], 0, 0, insert_done);
            if (match[2].length > params.padding)
                output += match[2];
            else
                output += padding;
            text = text.substr(match[0].length)
        }

        output += text;

        done(output, move_forward, move_up);
    }.bind(this);


    this.scriptlets['slugify'] = function(context, params, text, move_forward, move_up, done)
    {
        done(slugify(text.replace(/_/g, '-')), move_forward, move_up);
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

    $('#save-button').attr('disabled', true);
    var input = self.XMLEditorSelectedText(opts.context);
    window.setTimeout(function() {
        self.scriptlets[opts.action](opts.context, opts.extra, input, 0, 0, function(output, move_forward, move_up){
            /*if(timer)
                clearTimeout(timer);
            else */
            if (input != output) {
                self.XMLEditorReplaceSelectedText(opts.context, output)
            }
            if (move_forward || move_up) {
                try {
                    self.XMLEditorMoveCursorForward(opts.context, move_forward, move_up)
                }
                catch(e) {}
            }
            $.unblockUI({onUnblock: function() { $('#save-button').attr('disabled', null)}}); // done
        });
    }, 0);

}

ScriptletCenter.prototype.XMLEditorSelectedText = function(editor) {

    return editor.selection();
};

ScriptletCenter.prototype.XMLEditorReplaceSelectedText = function(editor, replacement)
{
	$progress.html("Replacing text");
	editor.replaceSelection(replacement);
};

ScriptletCenter.prototype.XMLEditorMoveCursorForward = function(panel, right, up) {
    var pos = panel.cursorPosition();
    if (up) {
        line = pos.line;
        while (up < 0) {
            line = panel.nextLine(line);
            ++up;
        }
        while (up > 0) {
            line = panel.prevLine(line);
            --up;
        }
        len = panel.lineContent(line).length;
        panel.selectLines(line, len + right);
    }
    else {
        panel.selectLines(pos.line, pos.character + right);
    }
};

var scriptletCenter;

$(function() {
    scriptletCenter = new ScriptletCenter();
});
