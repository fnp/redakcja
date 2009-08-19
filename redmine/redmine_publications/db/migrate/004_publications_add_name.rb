class PublicationsAddName < ActiveRecord::Migration
  def self.up
    add_column :publications, :name, :string
  end

  def self.down 
  end
end
