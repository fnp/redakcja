/*global Editor*/
Editor.MessageCenter = Editor.Object.extend({
  init: function() {
    this.messages = [];
    this.flashMessages = [];
    this.firstFlashMessage = null;
  },
  
  addMessage: function(type, text, flash) {
    this.messages.push({type: type, text: text});
    if (flash) {
      this.flashMessages.push({type: type, text: flash});
      if (this.flashMessages.length == 1) {
        this.set('firstFlashMessage', this.flashMessages[0]);
        setTimeout(this.changeFlashMessage.bind(this), 1000 * 10);
      }
    }
  },
  
  changeFlashMessage: function() {
    this.flashMessages.splice(0, 1);
    if (this.flashMessages.length > 0) {
      this.set('firstFlashMessage', this.flashMessages[0]);
      setTimeout(this.changeFlashMessage.bind(this), 1000 * 10);
    } else {
      this.set('firstFlashMessage', null);
    }
  }
  
});


var messageCenter = new Editor.MessageCenter();

