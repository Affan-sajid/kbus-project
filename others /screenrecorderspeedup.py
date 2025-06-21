from moviepy.editor import VideoFileClip

# === SETTINGS ===
input_file = "input.mp4"     # Rename your file to input.mp4 or change this
output_file = "output_fast.mp4"
speed_factor = 2.0            # 2x speed

# === PROCESSING ===
clip = VideoFileClip(input_file)
faster_clip = clip.fx(vfx.speedx, speed_factor)
faster_clip.write_videofile(output_file, codec="libx264")

print(f"✅ Done! Saved to {output_file}")
