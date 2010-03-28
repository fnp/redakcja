(function($){

    function normalizeNumber(number, length){
        // Numer strony musi być pomiędzy 1 a najwyższym numerem
        var pageCount = length;
        pageNumber = parseInt(pageNumber, 10);
        
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
    function ScanGalleryPerspective(doc, callback){
        var self = this;
		
		this.perspective_id = '';
		this.doc = doc;
        
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
            self.setPage(self.$numberInput.val() - 1);
        });
        
        $('.nexy-page', this.$element).click(function(){
            self.setPage(self.$numberInput.val() + 1);
        });        
        
        $('.zoom-in', this.$element).click(function(){
            self.alterZoom(0.2);
        });
        
        $('.zoom-out', this.$element).click(function(){
            self.alterZoom(-0.2);
        });
        
        $(window).resize(function(){
            self.dimensions.galleryWidth = self.$image.parent().width();
            self.dimensions.galleryHeight = self.$image.parent().height();
        });
        
        $('.gallery-image img', this.$element).load(function(){
			console.load("Image loaded.")
            self._resizeImage();
        });
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
        newPage = normalizeNumber(newPage, this.$image.length);
        this.$numberInput.val(newPage);
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
        
        var position = normalizePosition(this.$image.position().left, this.$image.position().top, this.dimensions.galleryWidth, this.dimensions.galleryHeight, this.dimensions.width, this.dimensions.height);
        
        this.$image.css({
            width: this.dimensions.width,
            height: this.dimensions.height,
            left: position.x,
            top: position.y
        });
    };
    
    /*
     * Loading gallery
     */
    ScanGalleryPerspective.prototype.onEnter = function(success, failure){
		var self = this;
		
        $.wiki.Perspective.prototype.onEnter.call(this);        
        
		this.doc.refreshGallery({
			success: function(doc, data) {
				self.$image.show();
				$('.error_message', self.$element).hide();
				success();				
			},
			failure: function(doc, message) {
				self.$image.hide();
				$('.error_message', self.$element).show().html(message);
				failure();				
			}			 
		});
    };
    
    $.wiki.ScanGalleryPerspective = ScanGalleryPerspective;
})(jQuery);


/*


 function onMouseMove(event){


 var position = normalizePosition(event.clientX - origin.x + imageOrigin.left, event.clientY - origin.y + imageOrigin.top, imageDimensions.galleryWidth, imageDimensions.galleryHeight, imageDimensions.width, imageDimensions.height);


 image.css({


 position: 'absolute',


 top: position.y,


 left: position.x


 });


 return false;


 }


 function onMouseUp(event){


 $(document).unbind('mousemove.gallery').unbind('mouseup.gallery');


 return false;


 }


 image.bind('mousedown', function(event){


 origin = {


 x: event.clientX,


 y: event.clientY


 };


 imageOrigin = image.position();


 $(document).bind('mousemove.gallery', onMouseMove).bind('mouseup.gallery', onMouseUp);


 return false;


 });


 if (url) {


 updateGallery(url);


 }


 }*/


