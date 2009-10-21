/*globals Editor fileId SplitView PanelContainerView EditorView FlashView messageCenter*/
Editor.Model = Editor.Object.extend({
    synced: false,
    data: null
});

Editor.ToolbarButtonsModel = Editor.Model.extend({
    className: 'Editor.ToolbarButtonsModel',
    buttons: {},
  
    init: function() {
        this._super();
    },
  
    load: function() {
        if (!this.get('buttons').length) {
            $.ajax({
                url: documentInfo.toolbarURL,
                dataType: 'json',
                success: this.loadSucceeded.bind(this)
            });
        }
    },
  
    loadSucceeded: function(data)
    {
        // do some escaping
        $.each(data, function() {
            $.each(this.buttons, function() {
                //do some lame escapes
                this.tooltip = this.tooltip.replace(/"/g, "&#34;");
            });
        });
        this.set('buttons', data);
    }
});


// Stany modelu:
//
//                  -> error -> loading
//                 /
// empty -> loading -> synced -> unsynced -> loading
//                           \
//                            -> dirty -> updating -> updated -> synced
//
Editor.XMLModel = Editor.Model.extend({
    _className: 'Editor.XMLModel',
    serverURL: null,
    data: '',
    state: 'empty',
  
    init: function(document, serverURL) {
        this._super();
        this.set('state', 'empty');
        this.set('revision', document.get('revision'));
        this.document = document;
        this.serverURL = serverURL;
        this.toolbarButtonsModel = new Editor.ToolbarButtonsModel();
        this.addObserver(this, 'data', this.dataChanged.bind(this));
    },
  
    load: function(force) {
        if (force || this.get('state') == 'empty') {
            this.set('state', 'loading');
            messageCenter.addMessage('info', 'xmlload', 'Wczytuję XML...');
            $.ajax({
                url: this.serverURL,
                dataType: 'text',
                data: {
                    revision: this.get('revision'),
                    user: this.document.get('user')
                    },
                success: this.loadingSucceeded.bind(this),
                error: this.loadingFailed.bind(this)
            });
            return true;
        }
        return false;
    },
  
    loadingSucceeded: function(data) {
        if (this.get('state') != 'loading') {
            alert('erroneous state:', this.get('state'));
        }
        this.set('data', data);
        this.set('state', 'synced');
        messageCenter.addMessage('success', 'xmlload', 'Wczytałem XML :-)');
    },
  
    loadingFailed: function(response)
    {
        if (this.get('state') != 'loading') {
            alert('erroneous state:', this.get('state'));
        }
        
        var message = parseXHRError(response);
        
        this.set('error', '<h2>Błąd przy ładowaniu XML</h2><p>'+message+'</p>');
        this.set('state', 'error');
        messageCenter.addMessage('error', 'xmlload', 'Nie udało mi się wczytać XML. Spróbuj ponownie :-(');
    },
  
    save: function(message) {
        if (this.get('state') == 'dirty') {
            this.set('state', 'updating');
            messageCenter.addMessage('info', 'xmlsave', 'Zapisuję XML...');
      
            var payload = {
                contents: this.get('data'),
                revision: this.get('revision'),
                user: this.document.get('user')
            };
            if (message) {
                payload.message = message;
            }
      
            $.ajax({
                url: this.serverURL,
                type: 'post',
                dataType: 'json',
                data: payload,
                success: this.saveSucceeded.bind(this),
                error: this.saveFailed.bind(this)
            });
            return true;
        }
        return false;
    },
  
    saveSucceeded: function(data) {
        if (this.get('state') != 'updating') {
            alert('erroneous state:', this.get('state'));
        }
        this.set('revision', data.revision);
        this.set('state', 'updated');
        messageCenter.addMessage('success', 'xmlsave', 'Zapisałem XML :-)');
    },
  
    saveFailed: function() {
        if (this.get('state') != 'updating') {
            alert('erroneous state:', this.get('state'));
        }
        messageCenter.addMessage('error', 'xmlsave', 'Nie udało mi się zapisać XML. Spróbuj ponownie :-(');
        this.set('state', 'dirty');
    },
  
    // For debbuging
    set: function(property, value) {
        if (property == 'state') {
            console.log(this.description(), ':', property, '=', value);
        }
        return this._super(property, value);
    },
  
    dataChanged: function(property, value) {
        if (this.get('state') == 'synced') {
            this.set('state', 'dirty');
        }
    },
  
    dispose: function() {
        this.removeObserver(this);
        this._super();
    }
});


Editor.HTMLModel = Editor.Model.extend({
    _className: 'Editor.HTMLModel',
    dataURL: null,
    htmlURL: null,
    renderURL: null,
    displaData: '',
    xmlParts: {},
    state: 'empty',
  
    init: function(document, dataURL, htmlURL) {
        this._super();
        this.set('state', 'empty');
        this.set('revision', document.get('revision'));        
        
        this.document = document;
        this.htmlURL = htmlURL;
        this.dataURL = dataURL;
        this.renderURL = documentInfo.renderURL;
        this.xmlParts = {};
    },
  
    load: function(force) {
        if (force || this.get('state') == 'empty') {
            this.set('state', 'loading');

            // load the transformed data
            // messageCenter.addMessage('info', 'Wczytuję HTML...');

            $.ajax({
                url: this.htmlURL,
                dataType: 'text',
                data: {
                    revision: this.get('revision'),
                    user: this.document.get('user')
                    },
                success: this.loadingSucceeded.bind(this),
                error: this.loadingFailed.bind(this)
            });
        }
    },    
  
    loadingSucceeded: function(data) {
        if (this.get('state') != 'loading') {
            alert('erroneous state:', this.get('state'));
        }
        this.set('data', data);
        this.set('state', 'synced');
    },
  
    loadingFailed: function(response) {
        if (this.get('state') != 'loading') {
            alert('erroneous state:', this.get('state'));
        }
        
        var err = parseXHRError(response);
        
        this.set('error', '<p>Nie udało się wczytać widoku HTML: </p>' + err.error_message);
        this.set('state', 'error');        
    },

    getXMLPart: function(elem, callback)
    {
        var path = elem.attr('wl2o:path');
        if(!this.xmlParts[path])
            this.loadXMLPart(elem, callback);
        else
            callback(path, this.xmlParts[path]);
    },

    loadXMLPart: function(elem, callback)
    {
        var path = elem.attr('wl2o:path');
        var self = this;

        $.ajax({
            url: this.dataURL,
            dataType: 'text',
            data: {
                revision: this.get('revision'),
                user: this.document.get('user'),
                chunk: path
                // format: 'nl'
            },
            success: function(data) {
                self.xmlParts[path] = data;
                console.log(data);
                callback(path, data);
            },
            // TODO: error handling
            error: function(data) {
                console.log('Failed to load fragment');
                callback(undefined, undefined);
            }
        });
    },

    putXMLPart: function(elem, data) {
        var self = this;
      
        var path = elem.attr('wl2o:path');
        this.xmlParts[path] = data;

        this.set('state', 'dirty');

        /* re-render the changed fragment */
        $.ajax({
            url: this.renderURL,
            type: "POST",
            dataType: 'text; charset=utf-8',
            data: {
                fragment: data,
                chunk: path
                // format: 'nl'
            },
            success: function(htmldata) {
                elem.html(htmldata);
                self.set('state', 'dirty');
            }
        });
    },

    save: function(message) {
        if (this.get('state') == 'dirty') {
            this.set('state', 'updating');

            var payload = {
                chunks: $.toJSON(this.xmlParts),
                revision: this.get('revision'),
                user: this.document.get('user')
            };

            if (message) {
                payload.message = message;
            }

            console.log(payload)

            $.ajax({
                url: this.dataURL,
                type: 'post',
                dataType: 'json',
                data: payload,
                success: this.saveSucceeded.bind(this),
                error: this.saveFailed.bind(this)
            });
            return true;
        }
        return false;
      
    },

    saveSucceeded: function(data) {
        if (this.get('state') != 'updating') {
            alert('erroneous state:', this.get('state'));
        }

        // flush the cache
        this.xmlParts = {};
    
        this.set('revision', data.revision);
        this.set('state', 'updated');
    },

    saveFailed: function() {
        if (this.get('state') != 'updating') {
            alert('erroneous state:', this.get('state'));
        }        
        this.set('state', 'dirty');
    },

    // For debbuging
    set: function(property, value) {
        if (property == 'state') {
            console.log(this.description(), ':', property, '=', value);
        }
        return this._super(property, value);
    }
});


Editor.ImageGalleryModel = Editor.Model.extend({
    _className: 'Editor.ImageGalleryModel',
    serverURL: null,
    data: [],
    state: 'empty',

    init: function(document, serverURL) {
        this._super();
        this.set('state', 'empty');
        this.serverURL = serverURL;
        // olewać data
        this.pages = [];
    },

    load: function(force) {
        if (force || this.get('state') == 'empty') {
            console.log("setting state");
            this.set('state', 'loading');
            console.log("going ajax");
            $.ajax({
                url: this.serverURL,
                dataType: 'json',
                success: this.loadingSucceeded.bind(this),
                error: this.loadingFailed.bind(this)
            });
        }
    },

    loadingSucceeded: function(data) 
    {
        console.log("success");        
        
        if (this.get('state') != 'loading') {
            alert('erroneous state:', this.get('state'));
        }

        console.log('galleries:', data);

        if (data.length === 0) {
            this.set('data', []);
        } else {            
            this.set('data', data[0].pages);
        }

        this.set('state', 'synced');
    },

    loadingFailed: function(data) {
        console.log("failed");

        if (this.get('state') != 'loading') {
            alert('erroneous state:', this.get('state'));
        }       

        this.set('state', 'error');
    },

    set: function(property, value) {
        if (property == 'state') {
            console.log(this.description(), ':', property, '=', value);
        }
        return this._super(property, value);
    }
});


Editor.DocumentModel = Editor.Model.extend({
    _className: 'Editor.DocumentModel',
    data: null, // name, text_url, revision, latest_shared_rev, parts_url, dc_url, size, merge_url
    contentModels: {},
    state: 'empty',
    errors: '',
    revision: '',
    user: '',
  
    init: function() {
        this._super();
        this.set('state', 'empty');        
    },
  
    load: function() {
        if (this.get('state') == 'empty') {
            this.set('state', 'loading');
            messageCenter.addMessage('info', 'docload', 'Ładuję dane dokumentu...');
            $.ajax({
                cache: false,
                url: documentInfo.docURL,
                dataType: 'json',
                success: this.successfulLoad.bind(this),
                error: this.failedLoad.bind(this)
            });
        }
    },
  
    successfulLoad: function(data) {
        this.set('data', data);
        this.set('state', 'synced');

        this.set('revision', data.revision);
        this.set('user', data.user);

        this.contentModels = {
            'xml': new Editor.XMLModel(this, data.text_url),
            'html': new Editor.HTMLModel(this, data.text_url, data.html_url),
            'gallery': new Editor.ImageGalleryModel(this, data.gallery_url)
        };        

        for (var key in this.contentModels) {
            this.contentModels[key].addObserver(this, 'state', this.contentModelStateChanged.bind(this));
        }

        this.error = '';

        messageCenter.addMessage('success', 'docload', 'Dokument załadowany poprawnie :-)');
    },

    failedLoad: function(response) {
        if (this.get('state') != 'loading') {
            alert('erroneous state:', this.get('state'));
        }
        
        var err = parseXHRError(response);
        this.set('error', '<h2>Nie udało się wczytać dokumentu</h2><p>'+err.error_message+"</p>");
        this.set('state', 'error');
    },
  
    contentModelStateChanged: function(property, value, contentModel) {
        if (value == 'dirty') {
            this.set('state', 'dirty');
            for (var key in this.contentModels) {
                if (this.contentModels[key].guid() != contentModel.guid()) {
                    this.contentModels[key].set('state', 'unsynced');
                }
            }
        } else if (value == 'updated') {
            this.set('state', 'synced');
            for (key in this.contentModels) {
                if (this.contentModels[key].guid() == contentModel.guid()) {
                    this.contentModels[key].set('state', 'synced');
                    this.revision = this.contentModels[key].get('revision');

                }
            }
            for (key in this.contentModels) {
                if (this.contentModels[key].guid() != contentModel.guid()) {
                    this.contentModels[key].set('revision', this.revision);
                    this.contentModels[key].set('state', 'empty');
                }
            }
        }
    },
  
    saveDirtyContentModel: function(message) {
        for (var key in this.contentModels) {
            if (this.contentModels[key].get('state') == 'dirty') {
                this.contentModels[key].save(message);
                break;
            }
        }
    },
  
    update: function() {
        this.set('state', 'loading');

        messageCenter.addMessage('info', 'doc_update',
            'Uaktualniam dokument...');
            
        $.ajax({
            url: this.data.merge_url,
            dataType: 'json',
            type: 'post',
            data: {
                type: 'update',
                revision: this.get('revision'),
                user: this.get('user')
            },
            complete: this.updateCompleted.bind(this),            
        });
    },
  
    updateCompleted: function(xhr, textStatus)
    {
        console.log(xhr.status, xhr.responseText);
        var response = parseXHRResponse(xhr);
        if(response.success)
        {
            if( (response.data.result == 'no-op')
             || (response.data.timestamp == response.data.parent_timestamp))
            {
                if( (response.data.revision) && (response.data.revision != this.get('revision')) )
                {
                    // we're out of sync
                    this.set('state', 'unsynced');
                    return;
                }
                
                messageCenter.addMessage('info', 'doc_update',
                    'Już posiadasz najbardziej aktualną wersję.');
                    this.set('state', 'synced');
                return;
            }

            // result: success
            this.set('revision', response.data.revision);
            this.set('user', response.data.user);

            messageCenter.addMessage('info', 'doc_update',
                'Uaktualnienie dokumentu do wersji ' + response.data.revision);

            for (var key in this.contentModels) {
                this.contentModels[key].set('revision', this.get('revision') );
                this.contentModels[key].set('state', 'empty');
            }

            this.set('state', 'synced');
            return;
        }

        // no success means trouble
        messageCenter.addMessage(response.error_level, 'doc_update', 
            response.error_message);       
        
        this.set('state', 'unsynced');
    },
  
    merge: function(message) {
        this.set('state', 'loading');
        messageCenter.addMessage('info', 'doc_merge',
            'Scalam dokument z głównym repozytorium...');
            
        $.ajax({
            url: this.data.merge_url,
            type: 'post',
            dataType: 'json',
            data: {
                type: 'share',
                revision: this.get('revision'),
                user: this.get('user'),
                message: message
            },
            complete: this.mergeCompleted.bind(this),
            success: function(data) {
                this.set('mergeData', data);
            }.bind(this)
        });
    },
  
    mergeCompleted: function(xhr, textStatus) {
        console.log(xhr.status, xhr.responseText);
        var response = parseXHRResponse(xhr);
        if(response.success)
        {
            if( (response.data.result == 'no-op')
             || (response.data.shared_timestamp == response.data.shared_parent_timestamp))
            {
                if( (response.data.revision) && (response.data.revision != this.get('revision')) )
                {
                    // we're out of sync
                    this.set('state', 'unsynced');
                    return;
                }

                messageCenter.addMessage('info', 'doc_merge',
                    'Twoja aktualna wersja nie różni się od ostatnio zatwierdzonej.');
                this.set('state', 'synced');
                return;
            }

            if( response.data.result == 'accepted')
            {
                messageCenter.addMessage('info', 'doc_merge',
                    'Prośba o zatwierdzenie została przyjęta i oczekuję na przyjęcie.');
                this.set('state', 'synced');
                return;
            }

            // result: success
            this.set('revision', response.data.revision);
            this.set('user', response.data.user);

            messageCenter.addMessage('info', 'doc_merge',
                'Twoja wersja dokumentu została zatwierdzona.');
            
            this.set('state', 'synced');
            return;
        }

        // no success means trouble
        messageCenter.addMessage(response.error_level, 'doc_merge',
            response.error_message);

        this.set('state', 'unsynced');
    },
  
    // For debbuging
    set: function(property, value) {
        if (property == 'state') {
            console.log(this.description(), ':', property, '=', value);
        }
        return this._super(property, value);
    }
});


var leftPanelView, rightPanelContainer, doc;

$(function()
{
    var flashView = new FlashView('#flashview', messageCenter);
    
    doc = new Editor.DocumentModel();

    EditorView = new EditorView('#body-wrap', doc);
    EditorView.freeze("<h1>Wczytuję dokument...</h1>");

    leftPanelView = new PanelContainerView('#left-panel-container', doc);
    rightPanelContainer = new PanelContainerView('#right-panel-container', doc);

    
});
