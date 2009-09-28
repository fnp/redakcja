function ScriptletCenter() {

    this.scriptlets = {
        {% for scriptlet in scriptlets %}
        "{{scriptlet.name}}": function(context, params) {
            {{scriptlet.code|safe}}
        },
        {% endfor %}

        _none: null
    };   
            
}

ScriptletCenter.prototype.XMLEditorSelectedText = function(panel) {
    return panel.contentView.editor.selection();
}

ScriptletCenter.prototype.XMLEditorReplaceSelectedText = function(panel, replacement)
{
    panel.contentView.editor.replaceSelection(replacement);
    /* TODO: fire the change event */
}

ScriptletCenter.prototype.XMLEditorMoveCursorForward = function(panel, n) {
    var pos = panel.contentView.editor.cursorPosition();
    panel.contentView.editor.selectLines(pos.line, pos.character + n);
}

scriptletCenter = new ScriptletCenter();