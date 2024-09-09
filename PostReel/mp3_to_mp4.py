from moviepy.editor import *

# Function to convert .mp3 to .mp4
def mp3_to_mp4(mp3_file, image_file, output_file, resolution=(1280, 720)):
    # Load audio
    audio = AudioFileClip(mp3_file)

    # Load image and resize it to match the video resolution
    video = ImageClip(image_file).set_duration(audio.duration).resize(newsize=resolution)
    
    # Set the audio of the video to the loaded mp3 file
    video = video.set_audio(audio)

    # Set the position of the image (optional: can be 'center', 'left', etc.)
    video = video.set_position('center')

    # Export the result as an mp4 file
    video.write_videofile(output_file, codec='libx264', fps=30, audio_codec="aac", ffmpeg_params=["-g", "30", "-flags", "+cgop"])

# Example usage
mp3_file = "audio.mp3"
image_file = "Herb_Brooks.jpeg"  # The image to be shown in the video
output_file = "output_video.mp4"

mp3_to_mp4(mp3_file, image_file, output_file)
