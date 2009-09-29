/*global View render_template panels */
var ImageGalleryView = View.extend({
  _className: 'ImageGalleryView',
  element: null,
  model: null,
  template: 'image-gallery-view-template',
  
  init: function(element, model, parent, template) 
  {
    this.currentPage = 0;
    
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
    $.log('updating pages', property, value);
    if( property == 'data')
    {        
        this.gotoPage(this.currentPage);        
        this.element.html(render_template(this.template, this));        
    }   
  },

  gotoPage: function(index) {
     if (index < 0) 
         index = 0;

     var n = this.model.get('pages').length;
     if (index >= n) index = n-1;

     this.currentPage = index;
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
  
  dispose: function() {
    this.model.removeObserver(this);
    this._super();
  }
});

// Register view
panels['gallery'] = ImageGalleryView;