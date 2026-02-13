from smile_id_core import Signature
import os
from dotenv import load_dotenv

load_dotenv()

# initialize
partner_id = os.getenv("SMILE_PARTNER_ID")
api_key = os.getenv("SMILE_API_KEY")

if not partner_id or not api_key:
    raise RuntimeError("Missing SMILE_ID_PARTNER_ID or SMILE_ID_API_KEY in .env")

signature = Signature(partner_id, api_key)

# Generate signature
signature_dict = signature.generate_signature("2026-01-22T00:00:00Z")

print(signature_dict)