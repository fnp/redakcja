
window.walk = (node, handler) ->
  if handler.text
    textHandler = handler.text
  else
    textHandler = handler

  switch node.nodeType
    when 1, 9, 11
      child = node.firstChild
      while child
        nxt = child.nextSibling
        walk(child, handler)
        child = nxt
    when 3
      textHandler node


window.wrapInTag = (regex, tagName) ->
  fun = (node) ->
    matches = []
    while m = regex.exec(node.nodeValue)
      matches.push [regex.lastIndex, m[0]]

    matches.reverse()

    for m in matches
      to = m[0]
      frm = m[0] - m[1].length

      node_rest = node.splitText(to)
      alien = node.splitText(frm)
      wrapper = node.ownerDocument.createElement tagName
      node.parentNode.insertBefore wrapper, node_rest
      wrapper.appendChild alien
    node


# window._test_xml_tools = ->
#   p = new DOMParser()
#   dom = p.parseFromString("<a><b>łuków</b><c>jakaś jeszcze ~</c></a>", 'text/xml')

#   walk(dom.firstChild, wrapInTag(ALIEN_REGEX, 'alien'))
#   dom


# window.ALIEN_REGEX = /[^a-zA-Z0-9ąćęłńóśźżĄĆĘŁŃÓŚŹŻ\s<>«»\\*_!,:;?&%."'=#()\/-]+/g
# " just for syntax coloring.
