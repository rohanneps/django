from sqlalchemy import Column, String, Integer, Sequence, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from db_helper.db_base import DBConnector
from GlobalVariables import (
								PROSPECT_TABLE,
								GOOGLE_RUN_DETAILS_TABLE,
								AMAZON_RUN_DETAILS_TABLE
							 )


db_connector_obj = DBConnector()
base = db_connector_obj.get_declarative_base()

class ProspectDetails(base):
	__tablename__ = PROSPECT_TABLE

	id = Column(Integer, Sequence('prospect_prospect_id_seq'), primary_key=True)
	name = Column(String)
	file_name = Column(String)							
	email_recipients = Column(String)					
	start_date = Column(DateTime)
	last_updated_date = Column(DateTime)
	status = Column(Boolean)
	run_count = Column(Integer)
	platform = Column(String)

class GoogleRunDetails(base):

	__tablename__ = GOOGLE_RUN_DETAILS_TABLE

	id = Column(Integer, Sequence('prospect_rundetails_id_seq'), primary_key=True)
	prospect_id = Column(Integer, ForeignKey('prospect_prospect.id'))
	prospect = relationship('ProspectDetails')
	date_time = Column(DateTime)
	file_size = Column(String, default='0 KB')
	total_pla_records = Column(Integer, default=0)
	total_showcase_records = Column(Integer, default=0)
	post_process_completed = Column(Boolean, default=False)
	batch_email_sent = Column(Boolean, default=False)


class AmazonRunDetails(base):

	__tablename__ = AMAZON_RUN_DETAILS_TABLE

	id = Column(Integer, Sequence('prospect_amazondetails_id_seq'), primary_key=True)
	prospect_id = Column(Integer, ForeignKey('prospect_prospect.id'))
	prospect = relationship('ProspectDetails')
	date_time = Column(DateTime)
	total_amazon_choices_records = Column(Integer, default=0)
	total_brands_related_records = Column(Integer, default=0)
	total_editorial_recommendations_records = Column(Integer, default=0)
	total_organic_records = Column(Integer, default=0)
	total_sponsored_records = Column(Integer, default=0)
	total_today_deals_records = Column(Integer, default=0)
	post_process_completed = Column(Boolean, default=False)
	batch_email_sent = Column(Boolean, default=False)