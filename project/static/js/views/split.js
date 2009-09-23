/*globals Class*/

var SplitView = Class.extend({
  leftPanelClass: 'splitview-left-panel',
  rightPanelClass: 'splitview-right-panel',
  splitterClass: 'splitview-splitter',
  overlayClass: 'splitview-overlay',
  element: null,
  
  init: function(element) {
    this.element = $(element);
    this.leftPanel = $(this.leftPanelClass, element);
    this.rightPanel = $(this.rightPanelClass, element);
    this.splitter = $(this.splitterClass, element);
    this.overlay = this._createOverlay(this.overlayClass);
    
    this.splitter.bind('mousedown.splitview', this.beginResize.bind(this));
  },
  
  _createOverlay: function(cssClass) {
    var pos = this.root.position();
    return $('<div />')
      .addClass(cssClass)
      .css({
        position: 'absolute',
        left: pos.left,
        top: pos.top,
        width: this.root.width(),
        height: this.root.height()
      })
      .hide()
      .appendTo(this.element);
  },
  
  beginResize: function(event) {
    this.hotspotX = event.pageX - this.splitter.position().left;
    
    $(document)
      .bind('mousemove.splitview', this.resizeChanged.bind(this))
      .bind('mouseup.splitview', this.endResize.bind(this));

    this.overlay.show();
    return false;
  },
  
  resizeChanged: function(event) {
    var old_width = this.overlay.width();
    var delta = event.pageX + this.hotspotX - old_width;

    if(old_width + delta < 12) delta = 12 - old_width;
    if(old_width + delta > $(window).width()) {
      delta = $(window).width() - old_width;
    }
    
    this.overlay.css({'width': old_width + delta});
    
    if(this.overlay.next) {
        var left = parseInt(this.overlay.next.css('left'), 10);
        this.overlay.next.css('left', left+delta);
    }
    return false;
  },

  endResize: function(event) {
    $(document)
      .unbind('mousemove.splitview')
      .unbind('mouseup.splitview');
    
    this.leftPanel.css({
      left: 0,
      right: this.hotspotX
    });

    this.rightPanel.css({
      left: this.hotspotX,
      right: 0
    });

    this.overlay.hide();
  },
  
  dispose: function() {
    this.splitter.unbind('mousedown.splitview');
  }
});

