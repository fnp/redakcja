class PublicationsAddRepoId < ActiveRecord::Migration
  def self.up
    add_column :publications, :repository_id, :integer, :null => false, :default => 0
  end

  def self.down 
  end
end
