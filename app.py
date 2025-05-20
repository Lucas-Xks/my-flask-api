from flask import Flask, jsonify, abort
import json
import os # For checking file existence

# Create an instance of the Flask application
app = Flask(__name__)

FAQ_FILE = 'faq.json' # Define the JSON file name as a constant

# --- Helper Functions ---
def load_faq_data():
    """
    Loads FAQ data from the JSON file.
    Includes error handling for file not found and JSON decoding issues.
    """
    # Check if the FAQ file exists
    if not os.path.exists(FAQ_FILE):
        # Log the error to the Flask application's logger (visible in the console)
        app.logger.error(f"Critical Error: The data file '{FAQ_FILE}' was not found.")
        # Abort the request with a 500 Internal Server Error
        # The description will be part of the JSON response defined in the errorhandler
        abort(500, description=f"Server configuration error: Data file '{FAQ_FILE}' is missing.")
    
    try:
        # Open the file with explicit UTF-8 encoding (good practice)
        with open(FAQ_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f) # Parse JSON data from the file
        return data
    except json.JSONDecodeError as e:
        # Log the specific JSON decoding error
        app.logger.error(f"JSON Decode Error in '{FAQ_FILE}': {e}")
        abort(500, description=f"Error decoding data from '{FAQ_FILE}'. Please check its format.")
    except Exception as e:
        # Catch any other potential errors during file loading
        app.logger.error(f"An unexpected error occurred while loading '{FAQ_FILE}': {e}")
        abort(500, description="An unexpected error occurred while trying to load data.")

# --- API Endpoints ---

@app.route('/health', methods=['GET'])
def health_check():
    """
    A simple health check endpoint.
    Returns a 200 OK status with a JSON message if the API is running.
    More advanced health checks could verify dependencies (e.g., database connection, file readability).
    """
    # For a slightly more useful health check, we can try loading the data file.
    # If load_faq_data() fails, it will abort, and the error handler will take over.
    # If it succeeds, we know the file is accessible and readable.
    try:
        load_faq_data() # Attempt to load data to check file accessibility and format
        return jsonify({"status": "ok", "message": "API is healthy and data file is accessible."}), 200
    except Exception as e:
        # If load_faq_data itself raises an unhandled exception before aborting (shouldn't happen with current setup)
        # or if there's another issue in this try block.
        app.logger.error(f"Health check failed: {e}")
        # Return a 503 Service Unavailable if the health check fails critically
        return jsonify({"status": "error", "message": "API is unhealthy or data source is unavailable."}), 503


@app.route('/api/faq', methods=['GET'])
def get_all_faq():
    """
    Returns all FAQ items from the loaded JSON data.
    """
    faq_data = load_faq_data() # Load data using the helper function
    return jsonify(faq_data), 200 # Return all data with a 200 OK status

@app.route('/api/faq/<string:faq_key>', methods=['GET'])
def get_specific_faq(faq_key):
    """
    Returns a specific FAQ item identified by its key in the URL.
    Example: A GET request to /api/faq/price_cut will call this function with faq_key = "price_cut".
    """
    faq_data = load_faq_data() # Load data
    
    # Check if the requested key exists in our FAQ data
    if faq_key in faq_data:
        return jsonify(faq_data[faq_key]), 200 # Return the specific item and 200 OK
    else:
        # If the key is not found, return a custom JSON error and a 404 Not Found status
        return jsonify({"error": "FAQ item not found", "requested_key": faq_key}), 404

# --- Error Handlers ---
# These functions define custom JSON responses for common HTTP errors.

@app.errorhandler(404)
def not_found_error(error):
    """
    Custom handler for 404 Not Found errors.
    Ensures API consumers receive a JSON response for this error.
    'error.description' contains the message passed to abort() or a default Flask message.
    """
    return jsonify({
        "error_code": "NOT_FOUND",
        "message": error.description or "The requested resource was not found on this server."
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """
    Custom handler for 500 Internal Server Error.
    Ensures API consumers receive a JSON response.
    'error.description' contains the message passed to abort().
    """
    return jsonify({
        "error_code": "INTERNAL_SERVER_ERROR",
        "message": error.description or "An unexpected error occurred on the server. Please try again later."
    }), 500

@app.errorhandler(405)
def method_not_allowed_error(error):
    """
    Custom handler for 405 Method Not Allowed errors.
    This occurs if a client tries to use an HTTP method (e.g., POST) on a route that only accepts GET.
    """
    return jsonify({
        "error_code": "METHOD_NOT_ALLOWED",
        "message": error.description or "The method is not allowed for the requested URL."
    }), 405


# --- Main Execution Block ---
if __name__ == '__main__':
    # app.run() starts the Flask development server.
    # debug=True enables debugging features:
    #   - Automatic reloader: Server restarts when code changes.
    #   - Interactive debugger: Shows detailed error pages in the browser (for development).
    #   IMPORTANT: Never run with debug=True in a production environment!
    # port=5001 specifies the port number the server will listen on.
    app.run(debug=True, port=5001)