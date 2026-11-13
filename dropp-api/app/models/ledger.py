from sqlalchemy import Column, String, BigInteger, ForeignKey
from app.models.base import BaseModel

class LedgerEntry(BaseModel):
    __tablename__ = "ledger_entries"
    
    dropp_id = Column(String, nullable=False, index=True)
    entry_type = Column(String, nullable=False) # ESCROW_HELD, ESCROW_RELEASED, FEE_EARNED, REFUND
    amount_minor = Column(BigInteger, nullable=False)
    currency = Column(String(3), nullable=False)
    meta_data = Column(String, nullable=True) # JSON string for extra info
