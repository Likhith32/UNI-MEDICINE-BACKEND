from app import create_app
from app.socket import socketio
import os
from dotenv import load_dotenv

# Load environment variables from project-level .env
load_dotenv()

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "1") == "1"

    print(f"\n🚀 Starting Telemedicine backend on http://127.0.0.1:{port}\n")

    # Use Socket.IO server (requires eventlet or gevent) for realtime features
    socketio.run(
        app,
        host="0.0.0.0",
        port=port,
        debug=debug_mode
    )
