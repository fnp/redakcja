class Caret {
    constructor(view) {
        let self = this;
        self.view = view;
        self.singleClick = false;
        
        let caret = this.element = $('<span id="caret"><textarea></textarea></span>');
        
        // When user writes into caret, add it to the document.
        $('textarea', caret).on('input', function() {
            let v = $(this).val();
            $(this).val('');
            self.insertChar(v);
            
        });
        
        // On click on x-node element, set caret position.
        self.view.on('click', '*[x-node]', function(e) {
            if (e.redakcja_caret_inserted) return;
            e.redakcja_caret_inserted = true;
            
            if (self.singleClick) {
                self.singleClick = false;
                return;
            }
            
            self.detach();
            
            var selection = window.getSelection();
            if (!selection.isCollapsed) return;
            
            self.singleClick = true;
            setTimeout(function() {
                if (self.singleClick) {
                    self.element.insertBefore(
                        selection.anchorNode.splitText(
                            selection.anchorOffset
                        )
                    )
                    self.focus();
                }
                self.singleClick = false;
            }, 250);
            
        });
        
        self.element.on('keydown', function(e) {
            console.log('KEY');
            
            // TODO:
            // delete selection?
            
            // cases:
            // we are in <akap> (no going up)
            // we are in <wyroznienie> (can go up)
            // we are next to <wyroznienie> (can go inside)
            
            switch (e.key) {
            case "ArrowRight":
                if (e.shiftKey) {
                    self.detach();
                    return;
                }
                
                self.moveRight();
                break;
            case "ArrowLeft":
                if (e.shiftKey) {
                    self.detach();
                    return;
                }
                
                self.moveLeft();
                break;
            case "ArrowUp":
                if (e.shiftKey) {
                    self.detach();
                    return;
                }
                break;
            case "ArrowDown":
                if (e.shiftKey) {
                    self.detach();
                    return;
                }
                break;
            case "Backspace":
                self.deleteBefore();
                break;
            case "Delete":
                self.deleteAfter();
                break;
            case "Enter":
                self.splitBlock();
                break;
                //                default:
                //                    console.log('key', e.key, e.code);
            }
        })
    }
    
    get attached() {
        return this.element.parent().length;
    }
    
    detach() {
        console.log(this.view);
        
        let p;
        if (this.attached) {
            p = this.element.parent()[0]
            this.element.detach();
            p.normalize()
        }
    }
    
    focus() {
        $("textarea", self.element).focus();
    }
    
    normalize() {
        this.element.parent()[0].normalize();
    }
    
    insertChar(ch) {
        $(document.createTextNode(ch)).insertBefore(this.element);
        this.normalize();
    }
    
    deleteBefore() {
        let contents = this.element.parent().contents();
        // Find the text before caret.
        let textBefore = contents[contents.index(this.element) - 1];
        
        // Should be text, but what if not?
        textBefore.textContent = textBefore.textContent.substr(0, textBefore.textContent.length - 1);
        this.normalize();
        
    }
    
    deleteAfter() {
        let contents = this.element.parent().contents();
        // Find the text after caret.
        let textAfter = contents[contents.index(this.element) + 1];
        textAfter.textContent = textAfter.textContent.substr(1);
    }
    
    splitBlock() {
        let splitter = this.element;
        let parent, newParent, splitIndex, index;
        
        while (!splitter.is('div[x-node]')) {
            parent = splitter.parent();
            splitIndex = parent.contents().index(splitter);
            newParent = parent.clone();
            index = parent.contents().length - 1;
            while (index >= splitIndex) {
                newParent.contents()[index].remove();
                --index;
            }
            while (index >= 0) {
                console.log(newParent, index);
                parent.contents()[index].remove();
                -- index;
            }
            newParent.insertBefore(parent);
            
            console.log('split', parent);
            splitter = parent;
        }
    }
    
    moveLeft() {
        this.move({
            move: -1,
            edge: (i, l) => {return !i;},
            enter: (l) => {return l - 1;},
            splitTarget: (t) => {return t.splitText(t.length - 1);},
            noSplitTarget: (t) => {return t.splitText(t.length);},
        })
    }
    
    moveRight() {
        this.move({
            move: 1,
            edge: (i, l) => {return i == l - 1;},
            enter: (l) => {return 0;},
            splitTarget: (t) => {return t.splitText(1);},
            noSplitTarget: (t) => {return t;},
        })
    }
    
    move(opts) {
        if (!this.attached) return;
        
        this.normalize();
        
        let contents = this.element.parent().contents();
        let index = contents.index(this.element);
        let target, moved, oldparent;
        
        let parent = this.element.parent()[0];
        
        if (opts.edge(index, contents.length)) {
            // We're at the end -- what to do?
            // can we go up?
            
            if (parent.nodeName == 'EM') {
                oldparent = parent;
                parent = parent.parentNode;
                contents = $(parent).contents();
                index = contents.index(oldparent);
            }
        }
        
        index += opts.move;
        target = contents[index];
        moved = false;
        
        while (target.nodeType == 1) {
            // we've encountered a node.
            // can we go inside?
            
            if (target.nodeName == 'EM') {
                // enter
                parent = $(target);
                contents = parent.contents();
                index = opts.enter(contents.length);
                target = contents[index];
                
                // what if it has no elements?
            } else {
                // skip
                index += opts.move; // again, what if end?
                target = contents[index];
                moved = true;
            }
            
            // if editable?
            // what if editable but empty?
            
        }
        
        if (target.nodeType == 3) {
            if (!moved) {
                target = opts.splitTarget(target);
            } else {
                target = opts.noSplitTarget(target);
            }
            
            this.element.insertBefore(target);
        }
        this.normalize();
        this.focus();
    }
}
