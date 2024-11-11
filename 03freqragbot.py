from __future__ import annotations
from typing import AsyncIterable
import fastapi_poe as fp
from fastapi import FastAPI
import uvicorn
import os
from query_llm import process_query

load_dotenv()
access_key=os.environ.get("POE_ACCESS_KEY") 

class FreqRagBot(fp.PoeBot):
    async def get_response(
        self, request: fp.QueryRequest
    ) -> AsyncIterable[fp.PartialResponse]:
        last_message = request.query[-1].content
        # last_message = last_message.lower()
        result =  process_query(last_message)
        yield fp.PartialResponse(text=result)

    async def get_settings(self, setting: fp.SettingsRequest) -> fp.SettingsResponse:
        return fp.SettingsResponse(
            introduction_message="Welcome to the Freqrag bot. Please ask me anything about the freqtrade documentation and i will answer it my best."
        )


bot = FreqRagBot()
app = fp.make_app(bot, access_key=access_key)
app.mount("/poe-chat",app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000,
	log_level="info")
