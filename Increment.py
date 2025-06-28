
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase (Replace 'serviceAccountKey.json' with your Firebase service account key)
cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred)

# Get Firestore database reference
db = firestore.client()

# Define collection and document
collection_name = "Inventory"
document_name = "Ledger"
product_name = "Coconut Oil"

# Reference to the document
doc_ref = db.collection(collection_name).document(document_name)

# Fetch document data
doc = doc_ref.get()

if doc.exists:
    data = doc.to_dict()
    print(data)
    if product_name in data:
        # Increment count
        doc_ref.update({f"{product_name}.count": firestore.Increment(1)})
        print(f"Count incremented for {product_name}.")
    else:
        print(f"Product '{product_name}' not found in document.")
else:
    print(f"Document '{document_name}' does not exist.")

