import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, render_template, jsonify, request
import threading
import time

# Initialize Firebase
cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred)

# Get Firestore database reference
db = firestore.client()

# Flask application
app = Flask(__name__)

# Global variable to store current product count
current_product_count = 0
current_profit = 0

# Configuration
COLLECTION_NAME = "Inventory"
DOCUMENT_NAME = "Ledger"
COST_DOC = 'cqlcsm1ccDdxGx1QR2bk'
PRODUCT_NAME = "Coconut Oil"
UPDATE_INTERVAL = 15  # seconds

def update_product_count():
    global current_product_count
    global current_profit
    while True:
        try:
            # Reference to the document
            doc_ref = db.collection(COLLECTION_NAME).document(DOCUMENT_NAME)
            cost_ref = db.collection('CostEntries').document(COST_DOC)
            # Fetch document data
            doc = doc_ref.get()
            cost = cost_ref.get()
            if doc.exists:
                data = doc.to_dict()
                if PRODUCT_NAME in data:
                    # Update the global current product count
                    current_product_count = data[PRODUCT_NAME].get('count', 0)
                    print(f"Updated count for {PRODUCT_NAME}: {current_product_count}")
                else:
                    print(f"Product '{PRODUCT_NAME}' not found in document.")
            else:
                print(f"Document '{DOCUMENT_NAME}' does not exist.")

            if cost.exists:
                cost_data = cost.to_dict()
                current_profit = cost_data.get('profit', 0)
        except Exception as e:
            print(f"Error updating product count: {e}")
        
        # Wait for the specified interval before next update
        time.sleep(UPDATE_INTERVAL)

@app.route('/')
def index():
    return render_template('IndustryDashboard.html')
@app.route('/cost-entry')
def cost_entry():
    return render_template('CostEntry.html')
@app.route('/ChatAi')
def ai_entry():
    return render_template('ChatWithAI.html')
@app.route('/get_product_count')
def get_product_count():
    global current_product_count
    global current_profit
    return jsonify({'count': current_product_count})

@app.route('/get_profit')
def get_profit():
    global current_profit
    return jsonify({'profit': current_profit})

def get_product_count():
    global current_profit
    return jsonify({'count': current_product_count})

def run_flask_app():
    # Start the background thread for updating product count
    count_thread = threading.Thread(target=update_product_count, daemon=True)
    count_thread.start()
    
    # Run Flask app
    app.run(debug=True, port=5000)

@app.route('/submit-cost', methods=['POST'])
def submit_cost():
    try:
        # Get the cost data from the request
        cost_data = request.json
        
        # Create a document in Firestore
        cost_ref = db.collection('CostEntries').document(COST_DOC)
        cost_ref.set(cost_data)
        
        return jsonify({
            'message': 'Cost entry submitted successfully!',
            'document_id': cost_ref.id
        }), 200
    
    except Exception as e:
        print(f"Error submitting cost: {e}")
        return jsonify({
            'message': 'Failed to submit cost entry',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    run_flask_app()

    