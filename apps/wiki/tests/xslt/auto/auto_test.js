var $ = require('jquery');
var fs = require('fs');
var exec = require('child_process').exec;
var pd = require('pretty-data').pd;
var ansidiff = require('ansidiff');


eval(fs.readFileSync(__dirname + '/../../../../../redakcja/static/js/wiki/xslt.js') + '');


function assertNodesEqual(lhs, rhs, areHTMLNodes) {

    function throwError() {
        throw new Error(ansidiff.chars(pd.xml(lhs), pd.xml(rhs)));
    }

    var lhsNode = $(lhs)[0],
        rhsNode = $(rhs)[0];

    if(areHTMLNodes) {
        var getMagicAttrsInfo = function(node) {
            var valuePrefix = 'x-attr-value-';
            var namePrefix = 'x-attr-name-';
            var startsWith = function(str, prefix) { return str.substr(0, prefix.length) === prefix; }
            var isNameAttribute = function(attr) { return startsWith(attr.name, namePrefix); }
            var isValueAttribute = function(attr) { return startsWith(attr.name, valuePrefix); }
            var extractId = function(attr) { return attr.name.split('-').pop(); }
            var temp = {};
            var toret = {map: {}, magicAttrsList: []};
            
            for(var i = 0; i < node.attributes.length; i++) {
                var attr = node.attributes[i];
                if(isNameAttribute(attr) || isValueAttribute(attr)) {
                    var id = extractId(attr);
                    temp[id] = typeof temp[id] === 'undefined' ? {} : temp[id];
                    if(isNameAttribute(attr))
                        temp[id]['name'] = attr.value;
                    else
                        temp[id]['value'] = attr.value;
                    toret.magicAttrsList.push(attr.name);
                }
            }

            Object.keys(temp).forEach(function(id) {
                var pair = temp[id];
                toret.map[pair.name] = typeof toret.map[pair.name] === 'undefined' ? toret.map[pair.name] = [] : toret.map[pair.name];
                toret.map[pair.name].push(pair.value);
            });
            
            return toret;
        }
    
        var removeAttrs = function(node, attrsNames) {
            attrsNames.forEach(function(name) {
                node.removeAttribute(name);
            });
        }
        
        var mapsEqual = function(map1, map2) {
            if(Object.keys(map1).length != Object.keys(map2).length)
                return false;        
            var arraysEqual = function(a1, a2) {return a1.slice().sort().join('') === a2.slice().sort().join('');}
            Object.keys(map1).forEach(function(key) {
                if(Object.keys(map2).indexOf(key) === -1 || !arraysEqual(map2[key], map1[key]))
                    return false;
            });
            return true;
        }
    
        var lhsMagicAttrsInfo = getMagicAttrsInfo(lhsNode),
            rhsMagicAttrsInfo = getMagicAttrsInfo(rhsNode);
        
        removeAttrs(lhsNode, lhsMagicAttrsInfo.magicAttrsList);
        removeAttrs(rhsNode, rhsMagicAttrsInfo.magicAttrsList);
        
        if(!mapsEqual(lhsMagicAttrsInfo.map, rhsMagicAttrsInfo.map))
            throwError();
    }
    
    if(!lhsNode.isEqualNode(rhsNode))
        throwError();
}

suite('wiki.tests.xslt.auto', function() {
        
        var tempFileName = '.temp.xml';
        var xsltStyleSheetPath = __dirname + '/../../../../../redakcja/static/xsl/wl2html_client.xsl';
        
        fs.readdirSync(__dirname + '/data/').forEach(function(fileName) {
            
            if(fileName === tempFileName)
                return;
            
            var ext = fileName.split('.').pop();
            if(ext !== 'html' && ext !== 'xml')
                return;

            var inputData = fs.readFileSync(__dirname + '/data/' + fileName) + '';
            
            if(ext === 'html') {
                test('[HTML->XML->HTML] ' + fileName, function(done) {
                    var result = html2text({
                        element: $(inputData)[0],
                        stripOuter: false,
                        success: function(generatedXML) {
                            fs.writeFileSync(tempFileName, generatedXML);
                            exec(['xsltproc', xsltStyleSheetPath, tempFileName].join(' ') , {}, 
                                function(error, stdout, stderr) {
                                    fs.unlinkSync(tempFileName);
                                    assertNodesEqual(inputData, stdout, true);
                                    done();
                            });
                        },
                        error: function(msg){throw msg;}
                    });
                });
            } else if(ext === 'xml') {
                test('[XML->HTML->XML] ' + fileName, function(done) {
                    var originalXML = $(inputData);
                    exec(['xsltproc', xsltStyleSheetPath, __dirname + '/data/' + fileName].join(' ') , {},
                        function(error, stdout, stderr) {
                            var generatedHTML = $(stdout);
                            var result = html2text({
                                element: generatedHTML[0],
                                stripOuter: false,
                                success: function(xmltext) {
                                    assertNodesEqual(inputData, xmltext);
                                    done();
                                },
                                error: function(msg){throw msg;}
                            });
                    });
                });
            }
        });
});


