class CreatePublications < ActiveRecord::Migration
  def self.up
    create_table :publications do |t|
      t.column :source_file, :string, :null => false
    end
  end

  def self.down
    drop_table :publications
  end
end
