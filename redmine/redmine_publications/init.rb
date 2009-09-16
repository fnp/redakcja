require 'redmine'

# Patches to the Redmine core.
require 'dispatcher'

Dispatcher.to_prepare :redmine_publications do
  require_dependency 'issue'
  
  #Guards against including the module multiple time (like in tests)
  # and registering multiple callbacks
  unless Issue.included_modules.include? RedminePublications::IssuePatch
    Issue.send(:include, RedminePublications::IssuePatch)
  end
end

require_dependency 'issue_publication_hook'

Redmine::Plugin.register :redmine_publications do
  name 'Publications managment plugin'
  author 'Łukasz Rekucki'
  description 'This plugn helps manage issues related to a publication.'
  version '0.0.9'

  # permission :view_issues_for_publication, :publications => :issues 

  settings :partial => 'settings/publications_settings',
      :default => { :tracker => '1', :pattern => '.*/[a-z_].xml', :editorurl => 'http://localhost/:pubid'}

  menu :application_menu, :publications, { :controller => 'publications', :action => 'index' }, :caption => 'Publikacje'

#  requires_redmine :version_or_higher => '0.8.0'	 

end

