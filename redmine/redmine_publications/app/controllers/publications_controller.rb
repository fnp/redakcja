class PublicationsController < ApplicationController
  unloadable

#  before_filter :authorize, :only => [:issues]

  def index
  	@publications = Publication.all
	respond_to do |format|	
	  format.html
	  format.xml { render :xml => @publications }
	  format.json { render :json => @publications }
	end
  end

  def refresh
	regexp = Regexp.new(Setting.plugin_redmine_publications[:pattern])
	Repository.all.each do |repo|
	  repo.entries.each do |entry|
	    match = entry.path.match(regexp)
            if match
	      Publication.find_or_create_by_name(:name => match[1], 
		:source_file => entry.path, :repository_id => repo.id)
            end
          end
        end	
  end

  def issues
	@publication = Publication.find_by_name(params[:pub])

	joins = "JOIN issue_publications ON (issues.id = issue_publications.issue_id)"
	conditions = ['issue_publications.publication_id = ? ', @publication.id ]
	@issues = Issue.all(:joins => joins, :conditions =>  conditions)
	respond_to do |format|
	  format.html
          format.xml do 
	    render :xml => @issues
          end

	  format.json do
	    headers['Content-Type'] = 'application/json'
	    render :json => @issues
	  end
        end
  end

  def redirect_to_platform
	render :text => ""
  end

  private

  def find_project
    @project = Project.find(params[:project_id])
  end

end
