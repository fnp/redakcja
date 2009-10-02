/*global View render_template panels */
var EditorView = View.extend({
  _className: 'EditorView',
  element: null,
  model: null,
  template: null,
  
  init: function(element, model, template) {
    this._super(element, model, template);
    
    this.quickSaveButton = $('#action-quick-save', this.element).bind('click.editorview', this.quickSave.bind(this));
    this.commitButton = $('#action-commit', this.element).bind('click.editorview', this.commit.bind(this));
    this.updateButton = $('#action-update', this.element).bind('click.editorview', this.update.bind(this));
    this.mergeButton = $('#action-merge', this.element).bind('click.editorview', this.merge.bind(this));
    
    this.model.addObserver(this, 'state', this.modelStateChanged.bind(this));
    this.modelStateChanged('state', this.model.get('state'));
      
    // Inicjalizacja okien jQuery Modal
    $('#commit-dialog', this.element).
    jqm({
        modal: true,
        onShow: this.loadRelatedIssues.bind(this)
    });
    
    $('#commit-dialog-cancel-button', this.element).click(function() {
        $('#commit-dialog-error-empty-message').hide();
        $('#commit-dialog').jqmHide();
    });   
    
    // $('#split-dialog').jqm({
    //      modal: true,
    //      onShow: $.fbind(self, self.loadSplitDialog)
    //  }).
    //  jqmAddClose('button.dialog-close-button');
    
    this.model.load();
  },
  
  quickSave: function(event) {
    this.model.saveDirtyContentModel();
  },
  
  commit: function(event) {
    $('#commit-dialog', this.element).jqmShow({callback: this.doCommit.bind(this)});
  },
  
  doCommit: function(message) {
    this.model.saveDirtyContentModel(message);
  },
  
  update: function(event) {
    this.model.update();
  },
  
  merge: function(event) {
    $('#commit-dialog', this.element).jqmShow({callback: this.doMerge.bind(this)});
  },
  
  doMerge: function(message) {
    this.model.merge(message);
  },
  
  loadRelatedIssues: function(hash) {
    var self = this;
    var c = $('#commit-dialog-related-issues');

    $('#commit-dialog-save-button').click(function(event, data)
    {
      if ($('#commit-dialog-message').val().match(/^\s*$/)) {
        $('#commit-dialog-error-empty-message').fadeIn();
      } else {
        $('#commit-dialog-error-empty-message').hide();
        $('#commit-dialog').jqmHide();

        var message = $('#commit-dialog-message').val();
        $('#commit-dialog-related-issues input:checked')
          .each(function() { message += ' refs #' + $(this).val(); });
        console.log("COMMIT APROVED", hash.t);
        hash.t.callback(message);
      }
      return false;
    });

    $("div.loading-box", c).show();
    $("div.fatal-error-box", c).hide();
    $("div.container-box", c).hide();
    
    $.getJSON(c.attr('ui:ajax-src') + '?callback=?',
    function(data, status)
    {
        var fmt = '';
        $(data).each( function() {
            fmt += '<label><input type="checkbox" checked="checked"';
            fmt += ' value="' + this.id + '" />' + this.subject +'</label>\n';
        });
        $("div.container-box", c).html(fmt);
        $("div.loading-box", c).hide();
        $("div.container-box", c).show();        
    });   
    
    hash.w.show();
  },
  
  modelStateChanged: function(property, value) {
    // Uaktualnia stan przycisków
    if (value == 'dirty') {
      this.quickSaveButton.attr('disabled', null);
      this.commitButton.attr('disabled', null);
      this.updateButton.attr('disabled', 'disabled');
      this.mergeButton.attr('disabled', 'disabled');
    } else if (value == 'synced') {
      this.quickSaveButton.attr('disabled', 'disabled');
      this.commitButton.attr('disabled', 'disabled');
      this.updateButton.attr('disabled', null);
      this.mergeButton.attr('disabled', null);      
    } else if (value == 'empty') {
      this.quickSaveButton.attr('disabled', 'disabled');
      this.commitButton.attr('disabled', 'disabled');
      this.updateButton.attr('disabled', 'disabled');
      this.mergeButton.attr('disabled', 'disabled');
    }
  },
  
  dispose: function() {
    $('#action-quick-save', this.element).unbind('click.editorview');
    $('#action-commit', this.element).unbind('click.editorview');
    $('#action-update', this.element).unbind('click.editorview');
    $('#action-merge', this.element).unbind('click.editorview');

    this.model.removeObserver(this);
    this._super();
  }
});
