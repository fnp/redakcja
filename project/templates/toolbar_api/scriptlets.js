function SciptletCenter() {

    this.scriptlets = {
        {% for scriptlet in scriptlets %}
        "{{scriptlet.name}}": function(context, params) {
            {{scriptlet.code|safe}}
        },
        {% endfor %}

        _none: null
    };
            
}

scriptletCenter = new ScriptletCenter();