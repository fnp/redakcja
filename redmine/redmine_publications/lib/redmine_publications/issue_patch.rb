module RedminePublications
  # Patches Redmine's Issues dynamically. Adds a +after_save+ filter.

  module IssuePatch
    def self.included(base) # :nodoc:
      base.extend(ClassMethods)
 
      base.send(:include, InstanceMethods)
 
      # Same as typing in the class
      base.class_eval do
        unloadable # Send unloadable so it will not be unloaded in development
 
 	validate :check_relations
	after_save :update_relations
      end
 
    end
    
    module ClassMethods
    end
    
    module InstanceMethods

      def publication_names	
	if not @pubnames
	  self.publications.map { |pub| pub.name }
        else
	  @pubnames        
	end
      end

      def publication_names=(value)
	@pubnames = value.sort!
      end

      def publications
        Publication.all( 
	  :joins => 
	    "JOIN issue_publications ON (issue_publications.publication_id = publications.id)",
 	  :conditions =>
	    ["issue_publications.issue_id = ? ", self.id] )	
      end

      def check_relations
	current_names = self.publication_names
	non_existant = []

	pubs =  Publication.find_all_by_name(current_names).map {|i| i.name}
	missing = current_names.select {|name| not pubs.include?name }

	if not missing.empty?
	  errors.add("publications", "Missing publication(s): " + missing.join(', '))
	end
     end

     def update_relations
	old = self.publications
	current_names = self.publication_names
	Rails.logger.info('[INFO] Updating relations: old= ' << old.inspect << ' current=' << current_names.inspect)

	# delete unused relations
	deleted = old.select { |v| not (current_names.include?(v.name)) }
	deleted.each do |pub| 
	  IssuePublication.delete_all(["issue_publications.issue_id = ? AND issue_publications.publication_id = ?", self.id, pub.id])
	end

	current_names.each do |name|	
	    pub = Publication.find_by_name(name)
	    IssuePublication.find_or_create_by_publication_id_and_issue_id(pub.id, self.id)
	end

        return true
     end

    end
  end
end
