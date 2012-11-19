(function() {

  window.walk = function(node, handler) {
    var child, nxt, textHandler, _results;
    if (handler.text) {
      textHandler = handler.text;
    } else {
      textHandler = handler;
    }
    switch (node.nodeType) {
      case 1:
      case 9:
      case 11:
        child = node.firstChild;
        _results = [];
        while (child) {
          nxt = child.nextSibling;
          walk(child, handler);
          _results.push(child = nxt);
        }
        return _results;
        break;
      case 3:
        return textHandler(node);
    }
  };

  window.wrapInTag = function(regex, tagName) {
    var fun;
    return fun = function(node) {
      var alien, frm, m, matches, node_rest, to, wrapper, _i, _len;
      matches = [];
      while (m = regex.exec(node.nodeValue)) {
        matches.push([regex.lastIndex, m[0]]);
      }
      matches.reverse();
      for (_i = 0, _len = matches.length; _i < _len; _i++) {
        m = matches[_i];
        to = m[0];
        frm = m[0] - m[1].length;
        node_rest = node.splitText(to);
        alien = node.splitText(frm);
        wrapper = node.ownerDocument.createElement(tagName);
        node.parentNode.insertBefore(wrapper, node_rest);
        wrapper.appendChild(alien);
      }
      return node;
    };
  };

}).call(this);
