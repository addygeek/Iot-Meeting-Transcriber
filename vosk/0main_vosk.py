import asyncio
import json
from fastapi import FastAPI, WebSocket
from datetime import datetime
import uvicorn
from vosk.stt_vosk1 import WakeSleepVosk

app = FastAPI()
stt = WakeSleepVosk(model_path="vosk-model-en-in-0.5")
stt.start_listener()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Frontend connected")
    last_status = None

    try:
        while True:
            transcripts = stt.get_transcripts()
            current_status = "transcribing" if stt.active else "idle"

            # Send new text
            for t in transcripts:
                await websocket.send_text(json.dumps({
                    "status": current_status,
                    "text": t,
                    "timestamp": datetime.utcnow().isoformat()
                }))

            # Send status update on change
            if current_status != last_status:
                await websocket.send_text(json.dumps({
                    "status": current_status,
                    "text": "",
                    "timestamp": datetime.utcnow().isoformat()
                }))
                last_status = current_status

            await asyncio.sleep(0.1)
    except Exception as e:
        print("WebSocket disconnected:", e)

if __name__ == "__main__":
    uvicorn.run("main_vosk:app", host="0.0.0.0", port=8000, reload=True)
