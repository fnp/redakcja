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
    @match_status = []

    regexp = Regexp.new(Setting.plugin_redmine_publications[:pattern])
    Publication.delete_all()
    repos = Repository.all
    if repos
      repos.each do |repo|
        repo_status = []
        if repo.entries
          repo.entries.each do |entry|
            match = entry.path.match(regexp)
            if match
              Publication.find_or_create_by_name(:name => match[1],
                :source_file => entry.path, :repository_id => repo.id)
              repo_status += [{:path => entry.path, :match => match[1], :matched => true}]
            else
              repo_status += [{:path => entry.path, :match =>nil, :matched => false}]
            end
          end
          @match_status += [{:repo => repo, :status => repo_status}]
        end
      end
	
      respond_to do |format|
        format.html
        format.xml { render :xml => @match_status}
        format.json { render :json => @match_status }
      end
    end
  end

  def issues
    @publication = Publication.find_by_name(params[:pub])

    joins = "JOIN issue_publications ON (issues.id = issue_publications.issue_id)"
    conditions = ['issue_publications.publication_id = ? ', @publication.id ]
    @issues = Issue.all(:joins => joins, :conditions =>  conditions)

    respond_to do |fmt| 
      fmt.json { render :json => @issues, :callback => params[:callback] }
    end
  end

  private

  def find_project
    @project = Project.find(params[:project_id])
  end

end
