/*global View render_template panels */
var ImageGalleryView = View.extend({
  _className: 'ImageGalleryView',
  element: null,
  model: null,
  template: 'image-gallery-view-template',
  
  init: function(element, model, parent, template) 
  {
    this.currentPage = -1;
    
    this._super(element, model, template);
    this.parent = parent;
       
    this.model
      .addObserver(this, 'data', this.modelDataChanged.bind(this))
      .addObserver(this, 'state', this.modelStateChanged.bind(this));
      
    //$('.image-gallery-view', this.element).html(this.model.get('data'));
    this.modelStateChanged('state', this.model.get('state'));
    this.model.load();
  },
  
  modelDataChanged: function(property, value) 
  {    
    if( property == 'data')
    {
        this.render();
        this.gotoPage(this.currentPage);
    }   
  },

  gotoPage: function(index) 
  {
     if (index < 0) 
         index = 0;
    
     var n = this.$pages.length;
     if (index >= n) index = n-1;

     if( (this.currentPage == index) )
         return;

     var cpage = this.$currentPage();

     if(cpage) {
         var offset = this.pageViewOffset(cpage);
         this.cleanPage(cpage);
     }
     
     this.currentPage = index;

     cpage = this.$currentPage()
     this.renderImage(cpage, cpage.attr('ui:model'));

     if(offset) {
         cpage.css({top: offset.y, left: offset.x});
     }

     var self = this;
     $('img', cpage).bind('load', function() {
        if(offset)
             self.setPageViewOffset(cpage, offset);
     });
     
     cpage.show();

     if(this.currentPage == n-1)
          this.$nextButton.attr('disabled', 'disabled');
     else
          this.$nextButton.removeAttr('disabled');

      if(this.currentPage == 0)
          this.$prevButton.attr('disabled', 'disabled');
      else
          this.$prevButton.removeAttr('disabled');

      this.$pageInput.val( (this.currentPage+1) );
  },
  
  modelStateChanged: function(property, value) {
    if (value == 'synced' || value == 'dirty') {
      this.parent.unfreeze();
    } else if (value == 'unsynced') {
      this.parent.freeze('Niezsynchronizowany...');
    } else if (value == 'loading') {
      this.parent.freeze('Ładowanie...');
    } else if (value == 'saving') {
      this.parent.freeze('Zapisywanie...');
    }
  },

  $currentPage: function() {
      if(this.currentPage >= 0 && this.currentPage < this.$pages.length)
          return $(this.$pages[this.currentPage]);
      else
          return undefined;
  },    

  cleanPage: function($page) {
    $page.hide();
    $('img', $page).unbind();
    
    $page.empty();
    
    this.setPageViewOffset($page, {x:0, y:0});
  },

  pageDragStart: function(event)
  {      
      this.dragStart = {x: event.clientX, y: event.clientY};
      $(window).bind('mousemove.imagedrag', this.pageDrag.bind(this));
      $(window).bind('mouseup.imagedrag', this.pageDragStop.bind(this));
      
      this.$currentPage().css('cursor', 'move');

      return false;
  },

  pageDrag: function(event)
  {
      if(!this.dragStart) return;

      var delta = {
           x: this.dragStart.x - event.clientX,
           y: this.dragStart.y - event.clientY };     

      var offset = this.pageViewOffset( $(this.$pages[this.currentPage]) );
      offset.x -= delta.x;
      offset.y -= delta.y;
      this.setPageViewOffset( $(this.$pages[this.currentPage]), offset);
      
      this.dragStart = {x: event.clientX, y: event.clientY };     
      return false;
  },

  pageDragStop: function(event) {
      this.$currentPage().css('cursor', 'auto');

      this.dragStart = undefined;
      $(window).unbind('mousemove.imagedrag');
      $(window).unbind('mouseup.imagedrag');

      return false;
  },

  pageViewOffset: function($page) {
      var left = parseInt($page.css('left'));
      var top = parseInt($page.css('top'));

      return {x: left, y: top};
  },

  setPageViewOffset: function($page, offset) {
      // check if the image will be actually visible
      // and correct
      var MARGIN = 30;

      var vp_width = this.$pageListRoot.width();
      var vp_height = this.$pageListRoot.height();
      
      var width = $page.outerWidth();
      var height = $page.outerHeight();      

      if( offset.x+width-MARGIN < 0 ) {
        // console.log('too much on the left', offset.x, -width)
        offset.x = -width+MARGIN;
      }
      
      // too much on the right
      if( offset.x > vp_width-MARGIN) {
          offset.x = vp_width-MARGIN;
          // console.log('too much on the right', offset.x, vp_width, width)
      }

      
      if( offset.y+height-MARGIN < 0)
        offset.y = -height+MARGIN;      

      if( offset.y > vp_height-MARGIN)
          offset.y = vp_height-MARGIN;               
      
      $page.css({left: offset.x, top: offset.y});           
  }, 
  
  renderImage: function(target, source) {
      target.html('<img src="'+source+'" />');
      $('img', target).
        css({
            'user-select': 'none',
            '-webkit-user-select': 'none',
            '-khtml-user-select': 'none',
            '-moz-user-select': 'none',
        }).
        attr('unselectable', 'on').
        mousedown(this.pageDragStart.bind(this));
  },

  render: function() {
      /* first unbind all */
      
      // this.pageListElement
      if(this.$nextButton) this.$nextButton.unbind();
      if(this.$prevButton) this.$prevButton.unbind();
      if(this.$jumpButton) this.$jumpButton.unbind();

      /* render */
      this.element.html(render_template(this.template, this));

      /* fetch important parts */
      this.$pageListRoot = $('.image-gallery-page-list', this.element);
      this.$pages = $('.image-gallery-page-container', this.$pageListRoot);

      this.$nextButton = $('.image-gallery-next-button', this.element);
      this.$prevButton = $('.image-gallery-prev-button', this.element);
      this.$pageInput = $('.image-gallery-current-page', this.element);

      /* re-bind events */
      this.$nextButton.click( this.nextPage.bind(this) );
      this.$prevButton.click( this.prevPage.bind(this) );

      this.$pageInput.change( this.jumpToPage.bind(this) );
  },

  jumpToPage: function() {     
        this.gotoPage(parseInt(this.$pageInput.val())-1);
  },
  
  nextPage: function() {
      this.gotoPage(this.currentPage + 1);    
  },

  prevPage: function() {
      this.gotoPage(this.currentPage - 1);
  },
  
  dispose: function() {
    this.model.removeObserver(this);
    this._super();
  }
});

// Register view
panels['gallery'] = ImageGalleryView;