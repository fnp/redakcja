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
    Publication.delete_all()

    repo = Repository.find(:first, :conditions => ['project_id = ?', Setting.plugin_redmine_publications[:project]] )

    Rails.logger.info('[INFO] Importing changes from ' << repo.url)
    Rails.logger.info('[INFO] Change list: ' << repo.changes.find(:all).inspect )

    @repo_status = []
    repo.changes.find(:all).each do |change|
        Rails.logger.info('[INFO] Importing change ' << change.path)
        match = change.path.match(regexp)
        if match
            Publication.find_or_create_by_name(:name => match[1],
                :source_file => change.path, :repository_id => repo.id)
              @repo_status += [{:path => change.path, :match => match[1], :matched => true}]
        else
              @repo_status += [{:path => change.path, :match => nil, :matched => false}]
        end
    end
	
    respond_to do |format|
        format.html
        format.xml { render :xml => @repo_status}
        format.json { render :json => @repo_status }
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
