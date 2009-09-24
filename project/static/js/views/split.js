/*globals Class*/

// Split view inspired by jQuery Splitter Plugin http://methvin.com/splitter/
var SplitView = Class.extend({
  splitbarClass: 'splitview-splitbar',
  activeClass: 'splitview-active',
  element: null,
  zombie: null,
  leftViewOffset: 0,
  
  // Cache
  _splitbarWidth: 0,
  
  init: function(element) {
    this.element = $(element).css('position', 'relative');
    this.views = $(">*", this.element[0]).css({
    	position: 'absolute', 			  // positioned inside splitter container
    	'z-index': 1,					        // splitbar is positioned above
    	'-moz-outline-style': 'none',	// don't show dotted outline
      overflow: 'auto'
    });
    
    this.leftView = $(this.views[0]);
    this.rightView = $(this.views[1]);
    this.splitbar = $(this.views[2] || '<div></div>')
      .insertAfter(this.leftView)
      .css({
        position: 'absolute',
        'user-select': 'none',
        '-webkit-user-select': 'none',
        '-khtml-user-select': 'none',
        '-moz-user-select': 'none',
        'z-index': 100
      })
      .attr('unselectable', 'on')
      .addClass(this.splitbarClass)
      .bind('mousedown.splitview', this.beginResize.bind(this));
    
    this._splitbarWidth = this.splitbar.outerWidth();
    
    // Solomon's algorithm ;-)
    this.resplit(this.element.width() / 2);
  },
    
  beginResize: function(event) {
    this.zombie = this.zombie || this.splitbar.clone(false).insertAfter(this.leftView);
    this.views.css("-webkit-user-select", "none"); // Safari selects A/B text on a move
    this.splitbar.addClass(this.activeClass);
    this.leftViewOffset = this.leftView[0].offsetWidth - event.pageX;
    
    $(document)
      .bind('mousemove.splitview', this.resizeChanged.bind(this))
      .bind('mouseup.splitview', this.endResize.bind(this));
  },
  
  resizeChanged: function(event) {
    var newPosition = event.pageX + this.leftViewOffset;
    newPosition = Math.max(0, Math.min(newPosition, this.element.width() - this._splitbarWidth));
    this.splitbar.css('left', newPosition);
  },

  endResize: function(event) {
    var newPosition = event.pageX + this.leftViewOffset;
    this.zombie.remove();
    this.zombie = null;
    this.resplit(newPosition);

    $(document)
      .unbind('mousemove.splitview')
      .unbind('mouseup.splitview');
  },

  resplit: function(newPosition) {
    newPosition = Math.max(0, Math.min(newPosition, this.element.width() - this._splitbarWidth));
    this.splitbar.css('left', newPosition);
    this.leftView.css({
      left: 0,
      width: newPosition
    });
    this.rightView.css({
      left: newPosition + this._splitbarWidth,
      width: this.element.width() - newPosition - this._splitbarWidth
    });
    if (!$.browser.msie) {
		  this.views.trigger("resize");
		}
  },
  
  dispose: function() {
    this.splitter.unbind('mousedown.splitview');
  }
});

