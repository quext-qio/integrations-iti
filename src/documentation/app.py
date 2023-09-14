import requests
from flask import Flask, jsonify, request
from flask_swagger_ui import get_swaggerui_blueprint

# --------------------------------------------------------------------------------------------
# Create the application instance
# --------------------------------------------------------------------------------------------
app = Flask(__name__)

# --------------------------------------------------------------------------------------------
# Create the Swagger UI blueprint
# --------------------------------------------------------------------------------------------
SWAGGER_URL="/swagger"
API_URL="/static/swagger.json"
BASE_URL = "https://integrations-api.stage.quext.io/"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Access API'
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

# --------------------------------------------------------------------------------------------
# Create a URL route in our application for "/" to validate the server is running
# --------------------------------------------------------------------------------------------
@app.route("/")
def home():
    return jsonify({
        "message": "Server of ITI is running successfully",
    })

# --------------------------------------------------------------------------------------------
# Create a URL route in our application for "/download-swagger" to download the Swagger JSON 
# file, this is useful for sharing the Swagger JSON file with other developers
# --------------------------------------------------------------------------------------------
@app.route("/download-swagger")
def download_swagger():
    # Create path for Swagger JSON
    swagger_json_url = "http://127.0.0.1:5000" + API_URL
    
    # Download the file
    response = requests.get(swagger_json_url)
    if response.status_code == 200:
        # Update the headers to force the browser to download the file
        headers = {
            "Content-Disposition": f"attachment; filename=swagger.json",
            "Content-Type": "application/json"
        }
        return response.content, 200, headers
    else:
        return jsonify({"error": "Error downloading Swagger JSON file"}), 500


# Start the server
if __name__ == "__main__":
    app.run(port = 5000, debug=True)