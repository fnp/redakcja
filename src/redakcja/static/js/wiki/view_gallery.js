(function($){

    function normalizeNumber(pageNumber, pageCount){
        // Page number should be >= 1, <= pageCount; 0 if pageCount = 0
        var pageNumber = parseInt(pageNumber, 10);

        if (!pageCount)
            return 0;

        if (!pageNumber ||
                isNaN(pageNumber) ||
                pageNumber == Infinity ||
                pageNumber == -Infinity ||
                pageNumber < 1)
            return 1;

        if (pageNumber > pageCount)
            return pageCount;

        return pageNumber;
    }

    function bounds(galleryWidth, galleryHeight, imageWidth, imageHeight){
        return {
            maxX: 0,
            maxY: 0,
            minX: galleryWidth - imageWidth,
            minY: galleryHeight - imageHeight
        }
    };

    function normalizePosition(x, y, galleryWidth, galleryHeight, imageWidth, imageHeight){
        var b = bounds(galleryWidth, galleryHeight, imageWidth, imageHeight);
        return {
            x: Math.min(b.maxX, Math.max(b.minX, x)),
            y: Math.min(b.maxY, Math.max(b.minY, y))
        }
    };

    function fixImageSize(){

    }

    /*
     * Perspective
     */
    function ScanGalleryPerspective(options){
        var old_callback = options.callback || function() { };

        this.vsplitbar = 'GALERIA';

        options.callback = function(){
            var self = this;

            this.dimensions = {};
            this.zoomFactor = 1;
	    if (this.config().page == undefined)
		this.config().page = CurrentDocument.galleryStart;
            this.$element = $("#side-gallery");
            this.$numberInput = $('.page-number', this.$element);

            // ...
            var origin = {};
            var imageOrigin = {};

            this.$image = $('.gallery-image img', this.$element).attr('unselectable', 'on');

            // button handlers
            this.$numberInput.change(function(event){
                event.preventDefault();
                self.setPage($(this).val());
            });
                    
	    $('.start-page', this.$element).click(function(){
		self.setPage(CurrentDocument.galleryStart);
	    });

            $('.previous-page', this.$element).click(function(){
                self.setPage(parseInt(self.$numberInput.val(),10) - 1);
            });

            $('.next-page', this.$element).click(function(){
                self.setPage(parseInt(self.$numberInput.val(),10) + 1);
            });

            $('.zoom-in', this.$element).click(function(){
                self.alterZoom(0.2);
            });

            $('.zoom-out', this.$element).click(function(){
                self.alterZoom((-0.2));
            });

            $('.ctrl-gallery-setstart', this.$element).click(function(e) {
                e.preventDefault();
                CurrentDocument.setGalleryStart(self.config().page);
            });
            $('.ctrl-gallery-edit', this.$element).click(function(e) {
                e.preventDefault();
                CurrentDocument.openGalleryEdit();
            });
            $('.ctrl-gallery-refresh', this.$element).click(function(e) {
                e.preventDefault();
                self.refreshGallery();
            });
            $('#gallery-chooser').on('show.bs.modal', function (event) {
                var modal = $(this);
                var datalist = modal.find('.modal-body');
                datalist.html('');
                self.doc.withGalleryList(function(galleries) {
                    console.log(galleries);
                    $.each(galleries, (i, gallery) => {
                        item = $('<div class="form-check"><label class="form-check-label"><input class="form-check-input" type="radio" name="gallery"></label></div>');
                        $('input', item).val(gallery);
                        $('label', item).append(gallery);
                        if (gallery == self.doc.galleryLink) {
                            item.addClass('text-primary')
                            $('input', item).prop('checked', true);
                        }
                        item.appendTo(datalist);
                    });
                    item = $('<div class="form-check"><label class="form-check-label"><input class="ctrl-none form-check-input" type="radio" name="gallery"><em class="text-secondary">brak</em></label></div>');
                    item.appendTo(datalist);
                    item = $('<div class="form-check"><label class="form-check-label"><input class="ctrl-new form-check-input" type="radio" name="gallery"><input class="ctrl-name form-control" placeholder="nowa"></label></div>');
                    item.appendTo(datalist);
                });
            })
            $('#gallery-chooser .ctrl-ok').on('click', function (event) {
                let item = $('#gallery-chooser :checked');
                let name;
                if (item.hasClass('ctrl-none')) {
                    name = '';
                }
                else if (item.hasClass('ctrl-new')) {
                    name = $('#gallery-chooser .ctrl-name').val();
                } else {
                    name = item.val();
                }
                
                self.doc.setGallery(name);
                $('#gallery-chooser').modal('hide');
                self.refreshGallery(function() {
                    self.setPage(1);
                });
            });

            $(window).resize(function(){
                self.dimensions.galleryWidth = self.$image.parent().width();
                self.dimensions.galleryHeight = self.$image.parent().height();
            });

            this.$image.load(function(){
                console.log("Image loaded.")
                self._resizeImage();
            }).bind('mousedown', function() {
				self.imageMoveStart.apply(self, arguments);
			});



			old_callback.call(this);
        };

        $.wiki.SidebarPerspective.call(this, options);
    };

    ScanGalleryPerspective.prototype = new $.wiki.SidebarPerspective();

    ScanGalleryPerspective.prototype._resizeImage = function(){
        var $img = this.$image;

        $img.css({
            width: '',
            height: ''
        });

        this.dimensions = {
            width: $img.width() * this.zoomFactor,
            height: $img.height() * this.zoomFactor,
            originWidth: $img.width(),
            originHeight: $img.height(),
		    galleryWidth: $img.parent().width(),
            galleryHeight: $img.parent().height()
        };

        if (!(this.dimensions.width && this.dimensions.height)) {
            setTimeout(function(){
                $img.load();
            }, 100);
        }

        var position = normalizePosition($img.position().left, $img.position().top, this.dimensions.galleryWidth, this.dimensions.galleryHeight, this.dimensions.width, this.dimensions.height);

        $img.css({
            left: position.x,
            top: position.y,
            width: $img.width() * this.zoomFactor,
            height: $img.height() * this.zoomFactor
        });
    };

    ScanGalleryPerspective.prototype.setPage = function(newPage){
        newPage = normalizeNumber(newPage, this.doc.galleryImages.length);
        this.$numberInput.val(newPage);
		this.config().page = newPage;
        $('.gallery-image img', this.$element).attr('src', this.doc.galleryImages[newPage - 1].url);
    };

    ScanGalleryPerspective.prototype.alterZoom = function(delta){
        var zoomFactor = this.zoomFactor + delta;
        if (zoomFactor < 0.2)
            zoomFactor = 0.2;
        if (zoomFactor > 2)
            zoomFactor = 2;
        this.setZoom(zoomFactor);
    };

    ScanGalleryPerspective.prototype.setZoom = function(factor){
        this.zoomFactor = factor;

        this.dimensions.width = this.dimensions.originWidth * this.zoomFactor;
        this.dimensions.height = this.dimensions.originHeight * this.zoomFactor;

        // var position = normalizePosition(this.$image.position().left, this.$image.position().top, this.dimensions.galleryWidth, this.dimensions.galleryHeight, this.dimensions.width, this.dimensions.height);

		this._resizeImage();
    };

	/*
	 * Movement
	 */
	ScanGalleryPerspective.prototype.imageMoved = function(event){
		event.preventDefault();

		// origin is where the drag started
		// imageOrigin is where the drag started on the image

		var newX = event.clientX - this.origin.x + this.imageOrigin.left;
		var newY = event.clientY - this.origin.y + this.imageOrigin.top;

		var position = normalizePosition(newX, newY, this.dimensions.galleryWidth, this.dimensions.galleryHeight, this.dimensions.width, this.dimensions.height);

		this.$image.css({
			left: position.x,
			top: position.y,
		});

		return false;
	};

	ScanGalleryPerspective.prototype.imageMoveStart = function(event){
		event.preventDefault();

		var self = this;

		this.origin = {
			x: event.clientX,
			y: event.clientY
		};

		this.imageOrigin = self.$image.position();
		$(document).bind('mousemove.gallery', function(){
			self.imageMoved.apply(self, arguments);
		}).bind('mouseup.gallery', function() {
			self.imageMoveStop.apply(self, arguments);
		});

		return false;
	};

	ScanGalleryPerspective.prototype.imageMoveStop = function(event){
		$(document).unbind('mousemove.gallery').unbind('mouseup.gallery');
	};

    /*
     * Loading gallery
     */
    ScanGalleryPerspective.prototype.refreshGallery = function(success, failure) {
        var self = this;
        this.doc.refreshGallery({
            success: function(doc, data){
                self.$image.show();
				console.log("gconfig:", self.config().page );
				self.setPage( self.config().page );
                $('#imagesCount').html("/" + doc.galleryImages.length);

                $('.error_message', self.$element).hide();
                if(success) success();
            },
            failure: function(doc, message){
                self.$image.hide();
                $('.error_message', self.$element).show().html(message);
                if(failure) failure();
            }
        });
    }

    ScanGalleryPerspective.prototype.onEnter = function(success, failure){
        $.wiki.SidebarPerspective.prototype.onEnter.call(this);
        this.refreshGallery(success, failure);
    };

	ScanGalleryPerspective.prototype.onExit = function(success, failure) {

	};

    $.wiki.ScanGalleryPerspective = ScanGalleryPerspective;

})(jQuery);
