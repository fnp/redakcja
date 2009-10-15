/*global Editor*/
Editor.MessageCenter = Editor.Object.extend({
    init: function() {
        this.messages = [];
        this.flashMessages = [];
        this.firstFlashMessage = null;
        this.timeout = null;
        console.log("MSC-init:", Date(), this);
    },
  
    addMessage: function(type, tag, text, flash)
    {
        if (!tag) tag = '#default'
        
        if (!flash) {
            flash = text;
        }

        this.messages.push({
            type: type,
            text: text
        });

        this.flashMessages.push({
            type: type,
            text: flash,
            tag: tag
        });

        if(this.timeout) {
            if(this.flashMessages[0] && (this.flashMessages[0].tag == tag))
            {
                clearTimeout(this.timeout);
                this.timeout = null;
                this.changeFlashMessage();
            }
        }       
        
        else {
            /* queue was empty at the start */
            if (this.flashMessages.length == 1) {
                console.log("MSC-added-fisrt", Date(), this);
                this.set('firstFlashMessage', this.flashMessages[0]);
                this.timeout = setTimeout(this.changeFlashMessage.bind(this), 3000);
            }

        }
        
    },
  
    changeFlashMessage: function() 
    {
        console.log("MSC-change", Date(), this);
        var previous = this.flashMessages.splice(0, 1);
        
        if (this.flashMessages.length > 0) 
        {
            console.log("MSC-chaning-first", Date(), this);
            this.set('firstFlashMessage', this.flashMessages[0]);            
            this.timeout = setTimeout(this.changeFlashMessage.bind(this), 3000);
        } else {
            console.log("MSC-emptying", Date(), this);
            this.set('firstFlashMessage', null);
        }
    }
  
});


var messageCenter = new Editor.MessageCenter();

