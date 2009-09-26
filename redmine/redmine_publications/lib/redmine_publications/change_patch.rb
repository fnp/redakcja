module RedminePublications
  # Patches Redmine's Issues dynamically. Adds a +after_save+ filter.

  module ChangePatch
    def self.included(base) # :nodoc:
      base.extend(ClassMethods)

      base.send(:include, InstanceMethods)

      # Same as typing in the class
      base.class_eval do
        unloadable # Send unloadable so it will not be unloaded in development
        after_save :update_publication
      end

    end

    module ClassMethods
    end

    module InstanceMethods

      def update_publication
        if self.action == 'A'
          regexp = Regexp.new(Setting.plugin_redmine_publications[:pattern])
          match = self.path.match(regexp)
          Rails.logger.info('[INFO] Adding publication: "' << match[1])
          Publication.find_or_create_by_name(:name => match[1],
            :source_file => self.path, :repository_id => self.changeset.repository.id )
        end      
      end
      
    end
    
  end


end
