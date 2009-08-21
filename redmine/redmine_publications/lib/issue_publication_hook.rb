# Provides a link to the document on the platform
class IssuesPublicationHook < Redmine::Hook::ViewListener

  def view_issues_show_details_bottom(context)
	# TODO: złapać wyjątek konwersji
	if context[:issue].tracker_id == Setting.plugin_redmine_publications[:tracker].to_i
          result = "<tr><td><b>Publication(s):</b></td><td>"
  	  names = context[:issue].publication_names {|name| "<span>" + name + "</span>"} 
	  result << names.join(', ')
	  result << "</td></tr>"
	end
  end

  def controller_issues_edit_before_save(context)
	if context[:issue].tracker.id == Setting.plugin_redmine_publications[:tracker].to_i
	  old_value = context[:issue].publication_names
	  new_value = context[:params][:publications].split(',').map { |n| n.strip }
	  context[:journal].details << JournalDetail.new(
		:property => 'attr', :prop_key => "publications", 
		:old_value => old_value.join(', '), 
		:value => new_value.join(', ') ) unless new_value==old_value
	  context[:issue].publication_names = new_value
	end
  end


  def controller_issues_new_after_save(context)
	if context[:issue].tracker.id == Setting.plugin_redmine_publications[:tracker].to_i
	  value = context[:params][:publications].split(',').map { |n| n.strip }
	  context[:issue].publication_names = value
	  context[:issue].save
	end
  end
	
  render_on :view_issues_form_details_bottom, :partial => 'issue_form_pub'
end
