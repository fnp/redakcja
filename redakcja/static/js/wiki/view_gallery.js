(function($){

    function normalizeNumber(pageNumber, pageCount){
        // Numer strony musi być pomiędzy 1 a najwyższym numerem
        var pageNumber = parseInt(pageNumber, 10);

        if (!pageNumber ||
        pageNumber == NaN ||
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

		this.noupdate_hash_onenter = true;

        options.callback = function(){
            var self = this;

            this.dimensions = {};
            this.zoomFactor = 1;
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

            $(window).resize(function(){
                self.dimensions.galleryWidth = self.$image.parent().width();
                self.dimensions.galleryHeight = self.$image.parent().height();
            });

            $('.gallery-image img', this.$element).load(function(){
                console.log("Image loaded.")
                self._resizeImage();
            }).bind('mousedown', function() {
				self.imageMoveStart.apply(self, arguments);
			});



			old_callback.call(this);
        };

        $.wiki.Perspective.call(this, options);
    };

    ScanGalleryPerspective.prototype = new $.wiki.Perspective();

    ScanGalleryPerspective.prototype._resizeImage = function(){
        var $img = this.$image;

        $img.css({
            width: null,
            height: null
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
        $('#imagesCount').html("/"+this.doc.galleryImages.length);
        this.$numberInput.val(newPage);
		this.config().page = newPage;
        $('.gallery-image img', this.$element).attr('src', this.doc.galleryImages[newPage - 1]);
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
        /* this.$image.css({
            width: this.dimensions.width,
            height: this.dimensions.height,
            left: position.x,
            top: position.y
        });*/
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
    ScanGalleryPerspective.prototype.onEnter = function(success, failure){
        var self = this;

        $.wiki.Perspective.prototype.onEnter.call(this);

        $('.vsplitbar').not('.active').trigger('click');

        this.doc.refreshGallery({
            success: function(doc, data){
                self.$image.show();
				console.log("gconfig:", self.config().page );
				self.setPage( self.config().page );

                $('.error_message', self.$element).hide();
                if(success) success();
            },
            failure: function(doc, message){
                self.$image.hide();
                $('.error_message', self.$element).show().html(message);
                if(failure) failure();
            }
        });

    };

	ScanGalleryPerspective.prototype.onExit = function(success, failure) {

	};

    $.wiki.ScanGalleryPerspective = ScanGalleryPerspective;

})(jQuery);
