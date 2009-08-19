# Provides a link to the document on the platform
class IssuesPublicationHook < Redmine::Hook::ViewListener

  def view_issues_show_details_bottom(context)
	# TODO: złapać wyjątek konwersji
	if context[:issue].tracker_id == Setting.plugin_redmine_publications['tracker'].to_i
          result = "<tr><td><b>Publication(s):</b></td><td>"
  	  names = context[:issue].publication_names {|name| "<span>" + name + "</span>"} 
	  result << names.join(', ')
	  result << "</td></tr>"
	end
  end

  def controller_issues_edit_before_save(context)
	if context[:issue].tracker_id == Setting.plugin_redmine_publications['tracker'].to_i
 	  pub_field = context[:params][:publications]
	  context[:issue].publication_names = pub_field.split(',').map { |n| n.strip }
	end
  end

  render_on :view_issues_form_details_bottom, :partial => 'issue_form_pub'
end
