(function($) {
    $.wikiapi = {};
    var noop = function() {
    };
    var noops = {
	success: noop,
	failure: noop
    };
    /*
     * Return absolute reverse path of given named view. (at least he have it
     * hard-coded in one place)
     *
     * TODO: think of a way, not to hard-code it here ;)
     *
     */
    function reverse() {
	var vname = arguments[0];
	var base_path = "/editor";

	if (vname == "ajax_document_text") {
	    var path = "/text/" + arguments[1] + '/';

	    if (arguments[2] !== undefined)
		path += arguments[2] + '/';

	    return base_path + path;
	}

        if (vname == "ajax_document_revert") {
            return base_path + "/revert/" + arguments[1] + '/';
        }


	if (vname == "ajax_document_history") {
	    return base_path + "/history/" + arguments[1] + '/';
	}

	if (vname == "ajax_document_scans") {
            return base_path + "/scans/" + arguments[1] + '/';
	}
	if (vname == "ajax_document_gallery") {
	    return base_path + "/gallery/" + arguments[1] + '/';
	}

	if (vname == "ajax_document_diff")
	    return base_path + "/diff/" + arguments[1] + '/';

        if (vname == "ajax_document_rev")
            return base_path + "/rev/" + arguments[1] + '/';

	if (vname == "ajax_document_pubmark")
	    return base_path + "/pubmark/" + arguments[1] + '/';

	if (vname == "ajax_cover_preview")
	    return "/cover/preview/";

	console.log("Couldn't reverse match:", vname);
	return "/404.html";
    };
    class Api {
        static csrf = $('input[name="csrfmiddlewaretoken"]').val();

        // TODO: Add waiting marker, error reporting.
        static post(url, data) {
            data['csrfmiddlewaretoken'] = this.csrf;
            $.ajax({
                url: url,
                type: "POST",
                data: data
            });
        }

        static get(url, callback) {
            $.ajax({
                url: url,
                type: "GET",
                success: function(data) {
                    callback(data);
                },
            });
        }

        static setGallery(id, gallery) {
            this.post(
                '/editor/set-gallery/' + id + '/',
                {gallery: gallery}
            )
        }
        static setGalleryStart(id, start) {
            this.post(
                '/editor/set-gallery-start/' + id + '/',
                {start: start}
            )
        }

        static openGalleryEdit(bookSlug) {
            window.open(
                '/documents/book/' + bookSlug + '/gallery/',
                '_blank'
            ).focus();
        }

        static withGalleryList(callback) {
            this.get(
                '/editor/galleries/',
                callback
            );
        }
    }

    /*
     * Document Abstraction
     */
    class WikiDocument {
        constructor(element_id) {
	    var meta = $('#' + element_id);
	    this.id = meta.attr('data-chunk-id');

	    this.revision = $("*[data-key='revision']", meta).text();
	    this.readonly = !!$("*[data-key='readonly']", meta).text();

	    this.bookSlug = $("*[data-key='book-slug']", meta).text();
	    this.scansLink = $("*[data-key='scans']", meta).text();
	    this.galleryLink = $("*[data-key='gallery']", meta).text();
            this.galleryStart = parseInt($("*[data-key='gallery-start']", meta).text());
            this.fullUri = $("*[data-key='full-uri']", meta).text();

	    this.text = null;
	    this.has_local_changes = false;
            this.active = true;
	    this._lock = -1;
	    this._context_lock = -1;
	    this._lock_count = 0;
        };

        triggerDocumentChanged() {
	    $(document).trigger('wlapi_document_changed', this);
        }

        /*
         * Fetch text of this document.
         */
        fetch(params) {
	    params = $.extend({}, noops, params);
	    var self = this;
	    $.ajax({
	        method: "GET",
	        url: reverse("ajax_document_text", self.id),
	        data: {"revision": self.revision},
	        dataType: 'json',
	        success: function(data) {
		    var changed = false;

		    if (self.text === null || self.revision !== data.revision) {
		        self.text = data.text;
                        $.wiki.undo.push(data.text);
		        self.revision = data.revision;
		        self.gallery = data.gallery;
		        changed = true;
		        self.triggerDocumentChanged();
		    };

		    self.has_local_changes = false;
		    params['success'](self, changed);
	        },
	        error: function() {
		    params['failure'](self, "Nie udało się wczytać treści dokumentu.");
	        }
	    });
        }

        /*
         * Fetch history of this document.
         */
        fetchHistory(params) {
	    /* this doesn't modify anything, so no locks */
	    params = $.extend({}, noops, params);
	    var self = this;
	    $.ajax({
	        method: "GET",
	        url: reverse("ajax_document_history", self.id) + "?before=" + params.before,
	        dataType: 'json',
	        success: function(data) {
		    params['success'](self, data);
	        },
	        error: function() {
		    params['failure'](self, "Nie udało się wczytać historii dokumentu.");
	        }
	    });
        }

        fetchDiff(params) {
	    /* this doesn't modify anything, so no locks */
	    var self = this;
	    params = $.extend({
	        'from': self.revision,
	        'to': self.revision
	    }, noops, params);
	    $.ajax({
	        method: "GET",
	        url: reverse("ajax_document_diff", self.id),
	        dataType: 'html',
	        data: {
		    "from": params['from'],
		    "to": params['to']
	        },
	        success: function(data) {
		    params['success'](self, data);
	        },
	        error: function() {
		    params['failure'](self, "Nie udało się wczytać porównania wersji.");
	        }
	    });
        }

        checkRevision(params) {
            /* this doesn't modify anything, so no locks */
            var self = this;
            let active = self.active;
            self.active = false;
            $.ajax({
                method: "GET",
                url: reverse("ajax_document_rev", self.id),
                data: {
                    'a': active,
                },
                dataType: 'text',
                success: function(data) {
                    if (data == '') {
                        if (params.error)
                            params.error();
                    }
                    else if (data != self.revision)
                        params.outdated();
                }
            });
        }

        refreshImageGallery(params) {
            if (this.galleryLink) {
                params = $.extend({}, params, {
                    url: reverse("ajax_document_gallery", this.galleryLink)
                });
            }
            this.refreshGallery(params);
        }

        refreshScansGallery(params) {
            if (this.scansLink) {
                params = $.extend({}, params, {
                    url: reverse("ajax_document_scans", this.scansLink)
                });
                this.refreshGallery(params);
            } else {
                // Fallback to image gallery.
                this.refreshImageGallery(params)
            }
        }
        
        /*
         * Fetch gallery
         */
        refreshGallery(params) {
	    params = $.extend({}, noops, params);
	    var self = this;
            if (!params.url) {
	        params.failure('Brak galerii.');
	        return;
            }
	    $.ajax({
	        method: "GET",
	        url: params.url,
	        dataType: 'json',
	        success: function(data) {
		    params.success(data);
	        },
	        error: function(xhr) {
                    switch (xhr.status) {
                    case 403:
                        var msg = 'Galerie dostępne tylko dla zalogowanych użytkowników.';
                        break;
                    case 404:
                        var msg = "Nie znaleziono galerii.";
                    default:
                        var msg = "Nie udało się wczytać galerii.";
                    }
		    params.failure(msg);
	        }
	    });
        }

        setGallery(gallery) {
            this.galleryLink = gallery;
            Api.setGallery(this.id, gallery);
        }

        setGalleryStart(start) {
            this.galleryStart = start;
            Api.setGalleryStart(this.id, start);
        }

        openGalleryEdit(start) {
            Api.openGalleryEdit(this.bookSlug);
        }

        withGalleryList(callback) {
            Api.withGalleryList(callback);
        }
        
        /*
         * Set document's text
         */
        setText(text, silent=false) {
            if (text == this.text) return;
            if (!silent) {
                $.wiki.undo.push(text);
            }
            this.text = text;
            this.has_local_changes = true;
        }

        undo() {
            let ctx = $.wiki.exitContext();
            this.setText(
                $.wiki.undo.undo(),
                true
            );
            $.wiki.enterContext(ctx);
        }
        redo() {
            let ctx = $.wiki.exitContext();
            this.setText(
                $.wiki.undo.redo(),
                true
            );
            $.wiki.enterContext(ctx);
        }

        /*
         * Save text back to the server
         */
        save(params) {
	    params = $.extend({}, noops, params);
	    var self = this;

	    if (!self.has_local_changes) {
	        console.log("Abort: no changes.");
	        return params['success'](self, false, "Nie ma zmian do zapisania.");
	    };

	    // Serialize form to dictionary
	    var data = {};
	    $.each(params['form'].serializeArray(), function() {
	        data[this.name] = this.value;
	    });

	    data['textsave-text'] = self.text;

	    $.ajax({
	        url: reverse("ajax_document_text", self.id),
	        type: "POST",
	        dataType: "json",
	        data: data,
	        success: function(data) {
		    var changed = false;

                    $('#header').removeClass('saving');

		    if (data.text) {
		        self.text = data.text;
		        self.revision = data.revision;
		        self.gallery = data.gallery;
		        changed = true;
		        self.triggerDocumentChanged();
		    };

		    params['success'](self, changed, ((changed && "Udało się zapisać :)") || "Twoja wersja i serwera jest identyczna"));
	        },
	        error: function(xhr) {
                    if ($('#header').hasClass('saving')) {
                        $('#header').removeClass('saving');
                        $.blockUI({
                            message: "<p>Nie udało się zapisać zmian. <br/><button onclick='$.unblockUI()'>OK</button></p>"
                        })
                    }
                    else {
                        try {
                            params['failure'](self, $.parseJSON(xhr.responseText));
                        }
                        catch (e) {
                            params['failure'](self, {
                                "__message": "<p>Nie udało się zapisać - błąd serwera.</p>"
                            });
                        };
                    }
	        }
	    });

            $('#save-hide').click(function(){
                $('#header').addClass('saving');
                $.unblockUI();
                $.wiki.blocking.unblock();
            });
        } /* end of save() */

        revertToVersion(params) {
            var self = this;
            params = $.extend({}, noops, params);

            if (params.revision >= this.revision) {
                params.failure(self, 'Proszę wybrać rewizję starszą niż aktualna.');
                return;
            }

            // Serialize form to dictionary
            var data = {};
            $.each(params['form'].serializeArray(), function() {
                data[this.name] = this.value;
            });

            $.ajax({
                url: reverse("ajax_document_revert", self.id),
                type: "POST",
                dataType: "json",
                data: data,
                success: function(data) {
                    if (data.text) {
                        self.text = data.text;
                        self.revision = data.revision;
                        self.gallery = data.gallery;
                        self.triggerDocumentChanged();

                        params.success(self, "Udało się przywrócić wersję :)");
                    }
                    else {
                        params.failure(self, "Przywracana wersja identyczna z aktualną. Anulowano przywracanie.");
                    }
                },
                error: function(xhr) {
                    params.failure(self, "Nie udało się przywrócić wersji - błąd serwera.");
                }
            });
        }

        pubmark(params) {
	    params = $.extend({}, noops, params);
	    var self = this;
	    var data = {
	        "pubmark-id": self.id,
	    };

	    /* unpack form */
	    $.each(params.form.serializeArray(), function() {
	        data[this.name] = this.value;
	    });

	    $.ajax({
	        url: reverse("ajax_document_pubmark", self.id),
	        type: "POST",
	        dataType: "json",
	        data: data,
	        success: function(data) {
		    params.success(self, data.message);
	        },
	        error: function(xhr) {
		    if (xhr.status == 403 || xhr.status == 401) {
		        params.failure(self, {
			    "__all__": ["Nie masz uprawnień lub nie jesteś zalogowany."]
		        });
		    }
		    else {
		        try {
			    params.failure(self, $.parseJSON(xhr.responseText));
		        }
		        catch (e) {
			    params.failure(self, {
			        "__all__": ["Nie udało się - błąd serwera."]
			    });
		        };
		    };
	        }
	    });
        }

        refreshCover(params) {
            var self = this;
	    var data = {
	        xml: self.text // TODO: send just DC
	    };
            $.ajax({
                url: reverse("ajax_cover_preview"),
                type: "POST",
                data: data,
                success: function(data) {
                    params.success(data);
                },
                error: function(xhr) {
                    // params.failure("Nie udało się odświeżyć okładki - błąd serwera.");
                }
            });
        }

        getLength(params) {
            params = $.extend({}, noops, params);
            var xml = this.text.replace(/\/(\s+)/g, '<br />$1');
            var parser = new DOMParser();
            var doc = parser.parseFromString(xml, 'text/xml');
            var error = $('parsererror', doc);

            if (error.length > 0) {
                throw "Not an XML document.";
            }
            $.xmlns["rdf"] = "http://www.w3.org/1999/02/22-rdf-syntax-ns#";
            $('rdf|RDF', doc).remove();
            if (params.noFootnotes) {
                $('pa, pe, pr, pt', doc).remove();
            }
	    if (params.noThemes) {
	        $('motyw', doc).remove();
            }
            var text = $(doc).text();
            text = $.trim(text.replace(/\s{2,}/g, ' '));
            return text.length;
        }

        /* Temporary workaround for relative images. */
        getBase() {
            return '/media/dynamic/images/' + this.galleryLink + '/';
        }
    }

    $.wikiapi.WikiDocument = WikiDocument;
})(jQuery);
