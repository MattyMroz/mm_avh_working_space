#!/usr/bin/env python3

"""
Streaming TTS example with subtitles.

This example is similar to the example basic_audio_streaming.py, but it shows
WordBoundary events to create subtitles using SubMaker.
"""

import asyncio

import edge_tts

TEXT = """REINKARNACJA NAJSILNIEJSZEGO BOGA MIECZA"""
VOICE = "pl-PL-ZofiaNeural"
OUTPUT_FILE = "1.mp3"
WEBVTT_FILE = "1.srt"


async def amain() -> None:
    """Main function"""
    communicate = edge_tts.Communicate(TEXT, VOICE)
    submaker = edge_tts.SubMaker()
    with open(OUTPUT_FILE, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])

    with open(WEBVTT_FILE, "w", encoding="utf-8") as file:
        file.write(submaker.generate_subs())


if __name__ == "__main__":
    loop = asyncio.get_event_loop_policy().get_event_loop()
    try:
        loop.run_until_complete(amain())
    finally:
        loop.close()

# import asyncio
# import edge_tts
# import time
# import wave


# async def generate_audio(subtitle, voice, output_file):
#     start_time = 0
#     communicate = edge_tts.Communicate(subtitle, voice)
#     with wave.open(output_file, 'wb') as wav_file:
#         async for chunk in communicate.stream():
#             if chunk["type"] == "audio":
#                 wav_file.writeframes(chunk["data"])
#             elif chunk["type"] == "WordBoundary":
#                 duration = chunk["offset"] - start_time
#                 if duration > 0:
#                     silence_chunk = edge_tts.get_silence_chunk(duration)
#                     wav_file.writeframes(silence_chunk)
#                 start_time = chunk["offset"]


# async def convert_subtitles_to_speech(subtitles_file, voice, output_file):
#     with open(subtitles_file, "r", encoding="utf-8") as file:
#         subtitles = file.readlines()

#     await generate_audio("", voice, output_file)

#     for subtitle in subtitles:
#         subtitle = subtitle.strip()
#         if subtitle:
#             await generate_audio(subtitle, voice, output_file)
#         else:
#             silence_duration = 1000
#             with wave.open(output_file, 'rb') as wav_file:
#                 framerate = wav_file.getframerate()
#                 nframes = wav_file.getnframes()
#                 current_time = nframes / float(framerate)
#                 silence_frames = int(silence_duration * framerate / 1000)
#                 empty_frame = b'\x00' * 2

#                 for _ in range(silence_frames):
#                     wav_file.writeframes(empty_frame)


# async def main():
#     voice = "pl-PL-ZofiaNeural"
#     subtitles_file = "1.srt"
#     output_file = "1.wav"
#     await convert_subtitles_to_speech(subtitles_file, voice, output_file)

# if __name__ == "__main__":
#     loop = asyncio.get_event_loop()
#     try:
#         loop.run_until_complete(main())
#     finally:
#         loop.close()
