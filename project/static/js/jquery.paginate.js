(function($) {
    
    var settings = {
            items: [],
            itemsPerPage: 20,
            page: 0
    };

    $.fn.filterItems = function(condition)
    {
        settings.items = $('p', this);

        if(condition) settings.items = settings.items.filter(function() {
            return condition( $(this).attr('title') );
        });

        var pageCount = Math.ceil(settings.items.length / settings.itemsPerPage);
        var buttons =  $('.page-nav-wrap button', this.parent());
        buttons.show().filter(function(i) { return i >= pageCount; }).hide();
        this.switchToPage();
    };

    $.fn.switchToPage = function(index)
    {
        index = index || settings.page;
        var start = index * settings.itemsPerPage;
        var end = start + settings.itemsPerPage;
        $('p', this).hide();
        
        var visibleItems = settings.items.filter(function(i) { return i >= start && i < end; });
        visibleItems.show();        
    }

    $.fn.paginate = function(options)
    {
        var list = this;                 

        // apply defaults
        if (options) $.extend(settings, options);
        settings.items = $('p', list);       

        var nav = $('<p class="page-nav-wrap"></p>');
        list.before(nav);
        var pageCount = Math.floor(settings.items.length / settings.itemsPerPage);
        var orphanCount = settings.items.length - (pageCount * settings.itemsPerPage);
        var button = null;

        for(var i=0; i < pageCount; i++)
        {
            button = $("<button type='button'>"+(i+1)+"</button>");
            button.bind('click', i, function(event) { list.switchToPage(event.data); });
            nav.append(button);            
        }        

        if(orphanCount > 0)
        {
            i = pageCount;
            button = $("<button type='button'>"+(i+1)+"</button>");
            button.bind('click', i, function(event) { list.switchToPage(event.data); });
            nav.append(button);            
        }

        list.filterItems(function(){return true;});
        list.switchToPage(0);
    };
})(jQuery);
