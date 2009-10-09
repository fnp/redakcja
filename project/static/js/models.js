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
                url: toolbarUrl,
                dataType: 'json',
                success: this.loadSucceeded.bind(this)
            });
        }
    },
  
    loadSucceeded: function(data) {
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
  
    init: function(serverURL, revision) {
        this._super();
        this.set('state', 'empty');
        this.set('revision', revision);
        this.serverURL = serverURL;
        this.toolbarButtonsModel = new Editor.ToolbarButtonsModel();
        this.addObserver(this, 'data', this.dataChanged.bind(this));
    },
  
    load: function(force) {
        if (force || this.get('state') == 'empty') {
            this.set('state', 'loading');
            messageCenter.addMessage('info', 'Wczytuję XML...');
            $.ajax({
                url: this.serverURL,
                dataType: 'text',
                data: {
                    revision: this.get('revision')
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
        messageCenter.addMessage('success', 'Wczytałem XML :-)');
    },
  
    loadingFailed: function() {
        if (this.get('state') != 'loading') {
            alert('erroneous state:', this.get('state'));
        }
        this.set('error', 'Nie udało się załadować panelu');
        this.set('state', 'error');
        messageCenter.addMessage('error', 'Nie udało mi się wczytać XML. Spróbuj ponownie :-(');
    },
  
    update: function(message) {
        if (this.get('state') == 'dirty') {
            this.set('state', 'updating');
            messageCenter.addMessage('info', 'Zapisuję XML...');
      
            var payload = {
                contents: this.get('data'),
                revision: this.get('revision')
            };
            if (message) {
                payload.message = message;
            }
      
            $.ajax({
                url: this.serverURL,
                type: 'post',
                dataType: 'json',
                data: payload,
                success: this.updatingSucceeded.bind(this),
                error: this.updatingFailed.bind(this)
            });
            return true;
        }
        return false;
    },
  
    updatingSucceeded: function(data) {
        if (this.get('state') != 'updating') {
            alert('erroneous state:', this.get('state'));
        }
        this.set('revision', data.revision);
        this.set('state', 'updated');
        messageCenter.addMessage('success', 'Zapisałem XML :-)');
    },
  
    updatingFailed: function() {
        if (this.get('state') != 'updating') {
            alert('erroneous state:', this.get('state'));
        }
        messageCenter.addMessage('error', 'Nie udało mi się zapisać XML. Spróbuj ponownie :-(');
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
  
    init: function(htmlURL, revision, dataURL) {
        this._super();
        this.set('state', 'empty');
        this.set('revision', revision);
        this.htmlURL = htmlURL;
        this.dataURL = dataURL;
        this.renderURL = "http://localhost:8000/api/render";
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
                    revision: this.get('revision')
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
        // messageCenter.addMessage('success', 'Wczytałem HTML :-)');
    },
  
    loadingFailed: function(response) {
        if (this.get('state') != 'loading') {
            alert('erroneous state:', this.get('state'));
        }

        var json_response = null;
        var message = "";

        try {
            json_response = $.evalJSON(response.responseText);

            if(json_response.reason == 'xml-parse-error') {

                message = json_response.message.replace(/(line\s+)(\d+)(\s+)/i,
                    "<a class='xml-editor-ref' href='#xml-$2-1'>$1$2$3</a>");

                message = message.replace(/(line\s+)(\d+)(\,\s*column\s+)(\d+)/i,
                    "<a class='xml-editor-ref' href='#xml-$2-$4'>$1$2$3$4</a>");

                
            }
            else {
                message = json_response.message || json_response.reason || "nieznany błąd.";
            }
        }
        catch (e) {
            message = response.statusText;
        }

        this.set('error', '<p>Nie udało się wczytać widoku HTML: </p>' + message);

        this.set('state', 'error');
        // messageCenter.addMessage('error', 'Nie udało mi się wczytać HTML. Spróbuj ponownie :-(');
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
                part: path
            },
            success: function(data) {
                self.xmlParts[path] = data;
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

        this.set('state', 'unsynced');

        /* re-render the changed fragment */
        $.ajax({
            url: this.renderURL,
            type: "POST",
            dataType: 'text; charset=utf-8',
            data: {
                fragment: data,
                part: path
            },
            success: function(htmldata) {
                elem.replaceWith(htmldata);
                self.set('state', 'dirty');
            }
        });
    },

    update: function(message) {
        if (this.get('state') == 'dirty') {
            this.set('state', 'updating');

            var payload = {
                chunks: $.toJSON(this.xmlParts),
                revision: this.get('revision')
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
                success: this.updatingSucceeded.bind(this),
                error: this.updatingFailed.bind(this)
            });
            return true;
        }
        return false;
      
    },

    updatingSucceeded: function(data) {
        if (this.get('state') != 'updating') {
            alert('erroneous state:', this.get('state'));
        }

        // flush the cache
        this.xmlParts = {};
    
        this.set('revision', data.revision);
        this.set('state', 'updated');
    },

    updatingFailed: function() {
        if (this.get('state') != 'updating') {
            alert('erroneous state:', this.get('state'));
        }
        messageCenter.addMessage('error', 'Uaktualnienie nie powiodło się', 'Uaktualnienie nie powiodło się');
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

    init: function(serverURL) {
        this._super();
        this.set('state', 'empty');
        this.serverURL = serverURL;
        // olewać data
        this.pages = [];
    },

    load: function(force) {
        if (force || this.get('state') == 'empty') {
            this.set('state', 'loading');
            $.ajax({
                url: this.serverURL,
                dataType: 'json',
                success: this.loadingSucceeded.bind(this)
            });
        }
    },

    loadingSucceeded: function(data) {
        if (this.get('state') != 'loading') {
            alert('erroneous state:', this.get('state'));
        }

        console.log('galleries:', data);

        if (data.length === 0) {
            this.set('data', []);
        } else {
            console.log('dupa');
            this.set('data', data[0].pages);
        }

        this.set('state', 'synced');
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
    data: null, // name, text_url, user_revision, latest_shared_rev, parts_url, dc_url, size, merge_url
    contentModels: {},
    state: 'empty',
  
    init: function() {
        this._super();
        this.set('state', 'empty');
        this.load();
    },
  
    load: function() {
        if (this.get('state') == 'empty') {
            this.set('state', 'loading');
            messageCenter.addMessage('info', 'Ładuję dane dokumentu...');
            $.ajax({
                cache: false,
                url: documentsUrl + fileId,
                dataType: 'json',
                success: this.successfulLoad.bind(this)
            });
        }
    },
  
    successfulLoad: function(data) {
        this.set('data', data);
        this.set('state', 'synced');
        this.contentModels = {
            'xml': new Editor.XMLModel(data.text_url, data.user_revision),
            'html': new Editor.HTMLModel(data.html_url, data.user_revision, data.text_url),
            'gallery': new Editor.ImageGalleryModel(data.gallery_url)
        };
        for (var key in this.contentModels) {
            this.contentModels[key].addObserver(this, 'state', this.contentModelStateChanged.bind(this));
        }
        messageCenter.addMessage('success', 'Dane dokumentu zostały załadowane :-)');
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
                    this.data.user_revision = this.contentModels[key].get('revision');
                }
            }
            for (key in this.contentModels) {
                if (this.contentModels[key].guid() != contentModel.guid()) {
                    this.contentModels[key].set('revision', this.data.user_revision);
                    this.contentModels[key].set('state', 'empty');
                }
            }
        }
    },
  
    saveDirtyContentModel: function(message) {
        for (var key in this.contentModels) {
            if (this.contentModels[key].get('state') == 'dirty') {
                this.contentModels[key].update(message);
                break;
            }
        }
    },
  
    update: function() {
        this.set('state', 'loading');
        messageCenter.addMessage('info', 'Uaktualniam dokument...');
        $.ajax({
            url: this.data.merge_url,
            dataType: 'json',
            type: 'post',
            data: {
                type: 'update',
                target_revision: this.data.user_revision
            },
            complete: this.updateCompleted.bind(this),
            success: function(data) {
                this.set('updateData', data);
            }.bind(this)
        });
    },
  
    updateCompleted: function(xhr, textStatus) {
        console.log(xhr.status, textStatus);
        if (xhr.status == 200) { // Sukces
            this.data.user_revision = this.get('updateData').revision;
            messageCenter.addMessage('info', 'Uaktualnienie dokumentu do wersji ' + this.get('updateData').revision,
                'Uaktualnienie dokumentu do wersji ' + this.get('updateData').revision);
            for (var key in this.contentModels) {
                this.contentModels[key].set('revision', this.data.user_revision);
                this.contentModels[key].set('state', 'empty');
            }
            messageCenter.addMessage('success', 'Uaktualniłem dokument do najnowszej wersji :-)');
        } else if (xhr.status == 202) { // Wygenerowano PullRequest (tutaj?)
        } else if (xhr.status == 204) { // Nic nie zmieniono
            messageCenter.addMessage('info', 'Nic się nie zmieniło od ostatniej aktualizacji. Po co mam uaktualniać?');
        } else if (xhr.status == 409) { // Konflikt podczas operacji
            messageCenter.addMessage('error', 'Wystąpił konflikt podczas aktualizacji. Pędź po programistów! :-(');
        } else if (xhr.status == 500) {
            messageCenter.addMessage('critical', 'Błąd serwera. Pędź po programistów! :-(');
        }
        this.set('state', 'synced');
        this.set('updateData', null);
    },
  
    merge: function(message) {
        this.set('state', 'loading');
        messageCenter.addMessage('info', 'Scalam dokument z głównym repozytorium...');
        $.ajax({
            url: this.data.merge_url,
            type: 'post',
            dataType: 'json',
            data: {
                type: 'share',
                target_revision: this.data.user_revision,
                message: message
            },
            complete: this.mergeCompleted.bind(this),
            success: function(data) {
                this.set('mergeData', data);
            }.bind(this)
        });
    },
  
    mergeCompleted: function(xhr, textStatus) {
        console.log(xhr.status, textStatus);
        if (xhr.status == 200) { // Sukces
            this.data.user_revision = this.get('mergeData').revision;
            for (var key in this.contentModels) {
                this.contentModels[key].set('revision', this.data.user_revision);
                this.contentModels[key].set('state', 'empty');
            }
            messageCenter.addMessage('success', 'Scaliłem dokument z głównym repozytorium :-)');
        } else if (xhr.status == 202) { // Wygenerowano PullRequest
            messageCenter.addMessage('success', 'Wysłałem prośbę o scalenie dokumentu z głównym repozytorium.');
        } else if (xhr.status == 204) { // Nic nie zmieniono
            messageCenter.addMessage('info', 'Nic się nie zmieniło od ostatniego scalenia. Po co mam scalać?');
        } else if (xhr.status == 409) { // Konflikt podczas operacji
            messageCenter.addMessage('error', 'Wystąpił konflikt podczas scalania. Pędź po programistów! :-(');
        } else if (xhr.status == 500) {
            messageCenter.addMessage('critical', 'Błąd serwera. Pędź po programistów! :-(');
        }
        this.set('state', 'synced');
        this.set('mergeData', null);
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
    documentsUrl = $('#api-base-url').text() + '/';
    toolbarUrl = $('#api-toolbar-url').text();

    doc = new Editor.DocumentModel();

    EditorView = new EditorView('#body-wrap', doc);
    EditorView.freeze();

    leftPanelView = new PanelContainerView('#left-panel-container', doc);
    rightPanelContainer = new PanelContainerView('#right-panel-container', doc);

    var flashView = new FlashView('#flashview', messageCenter);   
});
