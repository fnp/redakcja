class Publication < ActiveRecord::Base
  has_many :issues, :through => :issuepublications
  belongs_to :repository
end
