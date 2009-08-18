class Publication < ActiveRecord::Base
  has_many :issues, :through => :issuepublications
end
