# Provides a link to the document on the platform
class IssuesPublicationHook < Redmine::Hook::ViewListener
  def view_issues_show_details_bottom(context)
        result = "<tr><td><b>Source File(s):</b></td><td>"
	names = context[:issue].source_files.map {|name| "<span>" + name + "</span>"} 
	result << names.join(', ')
	result + "</td></tr>"
  end

  def controller_issues_edit_before_save(context)
	pub_field = context[:params][:issue_source_files]
	context[:issue].source_files = pub_field
  end

  render_on :view_issues_form_details_bottom, :partial => 'issue_form_pub'
end
