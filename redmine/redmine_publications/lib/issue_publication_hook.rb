# Provides a link to the document on the platform
class IssuesPublicationHook < Redmine::Hook::ViewListener

  def self.render_on(hook, options={})
    define_method hook do |context|
      if !options.include?(:if) || evaluate_if_option(options[:if], context)
        context[:controller].send(:render_to_string, {:locals => context}.merge(options))
      end
    end
  end

  private

  def evaluate_if_option(if_option, context)
    case if_option
    when Symbol
      send(if_option, context)
    when Method, Proc
      if_option.call(context)
    end
  end

  def is_pticket?(context)
    context[:issue].project_id == Setting.plugin_redmine_publications[:project].to_i
  end

  public

  render_on :view_issues_show_details_bottom, :partial => 'issue_view_pub', :if => :is_pticket?
  render_on :view_issues_form_details_bottom, :partial => 'issue_form_pub', :if => :is_pticket?

  #  names = context[:issue].publication_names {|name| "<span>" + name + "</span>"}
  #  result << names.join(', ')

  def controller_issues_edit_before_save(context)
    if is_pticket?context
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
    if is_pticket?context
      value = context[:params][:publications].split(',').map { |n| n.strip }
      context[:issue].publication_names = value
      context[:issue].save
    end
  end
end
