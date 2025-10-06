# main_vosk.py
import asyncio
import json
from fastapi import FastAPI, WebSocket
import uvicorn
from stt_vosk import WakeSleepVosk

app = FastAPI()
stt = WakeSleepVosk()
stt.start_stream()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Frontend connected")
    try:
        while True:
            transcripts = stt.get_transcripts()
            for t in transcripts:
                message = json.dumps({
                    "status": "transcribing" if stt.active else "idle",
                    "text": t
                })
                await websocket.send_text(message)
            await asyncio.sleep(0.1)
    except Exception as e:
        print("WebSocket disconnected:", e)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
