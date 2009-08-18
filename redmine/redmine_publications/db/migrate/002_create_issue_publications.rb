class CreateIssuePublications < ActiveRecord::Migration
  def self.up
    create_table :issue_publications do |t| 
	t.column :publication_id, :integer, :null => false
        t.column :issue_id, :intrger, :null => false
    end
  end

  def self.down
    drop_table :issue_publications
  end
end
