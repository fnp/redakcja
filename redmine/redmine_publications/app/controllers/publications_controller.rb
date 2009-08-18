
class PublicationsController < ApplicationController
  unloadable

  @@source_file_field_id = 1

  def issues
	logger.info "Searching for issues with document name = " + params[:pub] + "."
	joins = "JOIN issue_publications ON (issues.id = issue_publications.issue_id) JOIN publications ON (issue_publications.publication_id = publications.id)"

	conditions = ['publications.source_file = ? ', params[:pub] ]
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

end
