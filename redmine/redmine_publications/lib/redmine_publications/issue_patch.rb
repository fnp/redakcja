module RedminePublications
  # Patches Redmine's Issues dynamically. Adds a +after_save+ filter.

  module IssuePatch
    def self.included(base) # :nodoc:
      base.extend(ClassMethods)
 
      base.send(:include, InstanceMethods)
 
      # Same as typing in the class
      base.class_eval do
        unloadable # Send unloadable so it will not be unloaded in development
 
        after_save :update_relations
        # after_destroy :check_relations
 
        # Add visible to Redmine 0.8.x
        unless respond_to?(:visible)
          named_scope :visible, lambda {|*args| { :include => :project,
              :conditions => Project.allowed_to_condition(args.first || User.current, :view_issues) } }
        end
      end
 
    end
    
    module ClassMethods
    end
    
    module InstanceMethods
      def source_files
	if not @source_files
	  @source_files = self.lookup_source_files.map { |pub| pub.source_file }
        end
	@source_files        
      end

      def source_files=(value)
	@source_files = value
      end

      def lookup_source_files
        Publication.all( 
	  :joins => 
	    "JOIN issue_publications ON (issue_publications.publication_id = publications.id)",
 	  :conditions =>
	    [" issue_publications.issue_id = ? ", self.id] )	
      end
	
      def update_relations
        self.reload
	current_assocs = self.lookup_source_files
	new_assocs_names = self.source_files.split(' ')

	# delete unused relations
	deleted = current_assocs.select { |v| not (new_assocs_names.include?(v.source_file)) }
	deleted.each { |pub| IssuePublication.delete_all( 
  	  :contitions => ["issue_publications.issue_id = ? AND issue_publicatons.publication_id = ?",
		self.id, pub.id]) }

	new_assocs_names.each do |name|
		pub = Publication.find_or_create_by_source_file(name)
		IssuePublication.find_or_create_by_publication_id_and_issue_id(pub.id, self.id)
	end

        return true
      end

    end
  end
end
