import os
from app import create_app

# Instantiate the application through our factory
env_context = os.getenv("FLASK_ENV", "development")
app = create_app(env_context)

if __name__ == "__main__":
    # Determine ports dynamically for cloud hosting compatibility
    port = int(os.getenv("PORT", 5000))
    
    # Run the application instance
    app.run(
        host="0.0.0.0", 
        port=port, 
        debug=app.config["DEBUG"]
    )