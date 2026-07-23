# This file looks for new folders inside user uploads and converts them to reel if they are not already converted
import os
from text_to_audio import text_to_speech_file
import time
import subprocess

def text_to_audio(folder):
    print("TTA - ", folder)
    desc_path = f"user_uploads/{folder}/desc.txt"
    try:
        with open(desc_path) as f:
            text = f.read()
    except FileNotFoundError:
        print(f"ERROR - {folder}: desc.txt missing, skipping")
        return False
    if not text.strip():
        print(f"ERROR - {folder}: desc.txt empty, skipping")
        return False
    print(text, folder)
    try:
        text_to_speech_file(text, folder)
    except Exception as e:
        print(f"ERROR - {folder}: TTS failed - {e}")
        return False
    return True

def create_reel(folder):
    command = f'''ffmpeg -f concat -safe 0 -i user_uploads/{folder}/input.txt -i user_uploads/{folder}/audio.mp3 -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black" -c:v libx264 -c:a aac -shortest -r 30 -pix_fmt yuv420p static/reels/{folder}.mp4'''
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR - {folder}: FFmpeg failed - {e}")
        return False
    print("CR - ", folder)
    return True

if __name__ == "__main__":
    while True:
        print("Processing queue...")
        try:
            with open("done.txt", "r") as f:
                done_folders = f.readlines()
        except FileNotFoundError:
            done_folders = []
        done_folders = [f.strip() for f in done_folders]

        folders = os.listdir("user_uploads")
        for folder in folders:
            if folder not in done_folders:
                audio_ok = text_to_audio(folder)
                if not audio_ok:
                    continue  # don't attempt render, don't mark done — will retry next loop
                reel_ok = create_reel(folder)
                if not reel_ok:
                    continue  # same — retry next loop instead of silently marking done

                with open("done.txt", "a") as f:
                    f.write(folder + "\n")

        time.sleep(4)
