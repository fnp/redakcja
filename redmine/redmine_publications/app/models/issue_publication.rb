class IssuePublication < ActiveRecord::Base
  belongs_to :publication
  belongs_to :issue
end	
