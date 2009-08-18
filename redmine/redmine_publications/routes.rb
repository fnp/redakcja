connect 'publications/:pub',
	:controller => 'publications',
	:action => 'redirect_to_platform'

connect 'publications/:pub/:action', 
	:controller => 'publications',
	:format => 'html'
	
connect 'publications/:pub/:action.:format', 
	:controller => 'publications' 
