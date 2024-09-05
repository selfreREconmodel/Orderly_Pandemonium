# Note: This code includes a workaround for Linux-specific audio issues.
# On Linux, an ALSA (Advanced Linux Sound Architecture) related error was encountered:
# "ALSA lib pcm.c:8526:(snd_pcm_recover) underrun occurred"
#
# Symptoms on Linux without the workaround:
# 1. When repeatedly playing a sound, the perceived volume decreases over time.
# 2. The volume setting remains constant (verified with print(getvolume)).
# 3. The issue does not occur if the sound is reloaded before each play.
#
# Current workaround:
# current_sound = sound.Sound(self.sounds_dict[sound_names[current_index]], volume=current_volume)
# This line recreates the sound object before each play, effectively reloading the sound.
#
# This approach resolves the volume decrease issue on Linux systems.
# The root cause may be related to ALSA buffer management or its interaction with
# pygame/PsychoPy, but the exact mechanism is not fully understood due to limited
# familiarity with ALSA's interaction with these libraries.

import platform
from psychopy import prefs, sound, core, visual
from psychopy.hardware import keyboard
import os
from typing import Dict, Optional, List
import random

# Set audio preferences for PsychoPy
prefs.hardware["audioLatencyMode"] = 4  # Configure latency mode for audio
prefs.hardware["audioDevice"] = 4  # Select audio device
prefs.general["audioLib"] = ["ptb"]  # Use Psychtoolbox for audio library


class VolumeAdjuster:
    def __init__(
        self,
        sound_files: List[str],
        reference_sound_file: Optional[str] = None,
        sound_dir: str = "",
        increment_rate: float = 0.05,
        repeat_rate: float = 1.0,
        start_value: float = 0.1,
        reference_sound_volume: Optional[float] = None,
        slider_style: str = "rating",
        lang: str = "en",
        shuffle: bool = True,
    ):
        self.is_windows = platform.system() == "Windows"  # Check if running on Windows
        self.sounds_dict = self._load_sounds(sound_files, sound_dir)
        self.reference_sound_file = (
            os.path.join(sound_dir, reference_sound_file)
            if reference_sound_file
            else None
        )
        self.reference_sound_volume = reference_sound_volume
        self.increment_rate = increment_rate
        self.repeat_time = 1 / repeat_rate
        self.start_value = start_value
        self.slider_style = slider_style
        self.clock = core.Clock()  # Create a clock for timing
        self.kb = keyboard.Keyboard()  # Initialize keyboard for input
        self.lang = lang
        self.shuffle = shuffle

        # Preload reference sound for Windows
        if self.is_windows and self.reference_sound_file:
            self.reference_sound = sound.Sound(
                self.reference_sound_file, volume=reference_sound_volume
            )

    def _load_sounds(self, sound_files: List[str], sound_dir: str) -> Dict[str, any]:
        # For Windows, preload sounds. For Linux, store file paths.
        if self.is_windows:
            return {
                os.path.splitext(os.path.basename(f))[0]: sound.Sound(
                    os.path.join(sound_dir, f)
                )
                for f in sound_files
            }
        else:
            return {
                os.path.splitext(os.path.basename(f))[0]: os.path.join(sound_dir, f)
                for f in sound_files
            }

    def _create_instruction_text(self, win: visual.Window) -> visual.TextStim:
        # Create instruction text based on language setting
        if self.lang == "en":
            instructions = (
                "Adjust the volume using UP/DOWN arrow keys or by moving the mouse.\n"
                "Press '1' to play the current sound.\n"
                "Press 'SPACE' to move to the next sound.\n"
                "Press 'ESCAPE' to exit the application.\n"
                + "Play reference sound: 2\n"
                if self.reference_sound_file
                else ""
            )
        elif self.lang == "fr":
            instructions = (
                "Ajustez le volume avec les flèches HAUT/BAS ou en déplaçant la souris.\n"
                "Appuyez sur '1' pour lire le son actuel.\n"
                "Appuyez sur 'ESPACE' pour passer au son suivant.\n"
                "Appuyez sur 'ÉCHAP' pour quitter l'application.\n"
                + "Appuyez sur '2' pour lire le son de référence."
                if self.reference_sound_file
                else ""
            )

        return visual.TextStim(
            win,
            text=instructions,
            pos=(0, 0.4),
            height=0.05,
            color="black",
            font="Arial",
            wrapWidth=1.5,
        )

    def _create_slider(self, win: visual.Window) -> visual.Slider:
        # Create a slider for adjusting volume
        return visual.Slider(
            win,
            size=(1.2, 0.1),
            pos=(0, -0.2),
            style=self.slider_style,
            labels=[
                "10%",
                "20%",
                "30%",
                "40%",
                "50%",
                "60%",
                "70%",
                "80%",
                "90%",
                "100%",
            ],
            labelHeight=0.05,
            startValue=self.start_value,
            granularity=0.001,
            ticks=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            fillColor="darkblue",
            borderColor="white",
            labelColor="black",
            font="Arial",
        )

    def _handle_key_press(
        self, key: str, last_key: Optional[str], last_time: Optional[float]
    ) -> tuple:
        # Update last_key and last_time based on key press
        if key == "2" and self.reference_sound_file:
            last_key = "2" if last_key != "2" else None
            last_time = self.clock.getTime() if last_key == "2" else None
        elif key == "1":
            last_key = "1" if last_key != "1" else None
            last_time = self.clock.getTime() if last_key == "1" else None
        return last_key, last_time

    def _update_volume(self, slider: visual.Slider) -> None:
        # Adjust slider value based on key inputs
        current_rating = slider.getRating() or self.start_value
        if self.kb.getState("up"):
            slider.setValue(min(current_rating + self.increment_rate, 1.0))
        elif self.kb.getState("down"):
            slider.setValue(max(current_rating - self.increment_rate, 0.0))

    def adjust_volume(self) -> Dict[str, float]:
        # Main loop for adjusting volume of sounds
        win = visual.Window(fullscr=True, color="lightgray")
        vol_slider = self._create_slider(win)
        instructions = self._create_instruction_text(win)
        current_sound_text = visual.TextStim(
            win,
            text="",
            pos=(0, 0.2),
            height=0.05,
            color="darkblue",
            font="Arial Bold",
        )

        sound_names = list(self.sounds_dict.keys())
        if self.shuffle:
            random.shuffle(sound_names)
        current_index = 0
        current_sound = (
            None
            if not self.is_windows
            else self.sounds_dict[sound_names[current_index]]
        )

        slider_vol = {}
        last_key = None
        last_time = None
        total_sounds = len(self.sounds_dict)

        while current_index < len(self.sounds_dict):
            current_sound_text.text = (
                f"Progress: {current_index}/{total_sounds} completed"
            )

            vol_slider.draw()
            instructions.draw()
            current_sound_text.draw()
            win.flip()

            if self.kb.getKeys(["escape"]):
                break

            self._update_volume(vol_slider)
            current_volume = vol_slider.getRating() or self.start_value

            if self.is_windows:
                current_sound.setVolume(current_volume)

            keys = self.kb.getKeys(["1", "2", "space"])
            for key in keys:
                if key.name in ["1", "2"]:
                    last_key, last_time = self._handle_key_press(
                        key.name, last_key, last_time
                    )
                elif key.name == "space":
                    slider_vol[sound_names[current_index]] = current_volume
                    current_index += 1
                    if current_index < len(self.sounds_dict):
                        if self.is_windows:
                            current_sound = self.sounds_dict[sound_names[current_index]]
                        vol_slider.reset()

            # Play reference or current sound based on key press
            if (
                last_key == "2"
                and self.reference_sound_file
                and (self.clock.getTime() - last_time) >= self.repeat_time
            ):
                if self.is_windows:
                    self.reference_sound.play()
                else:
                    reference_sound = sound.Sound(
                        self.reference_sound_file, volume=self.reference_sound_volume
                    )
                    reference_sound.play()
                last_time = self.clock.getTime()
            elif (
                last_key == "1"
                and (self.clock.getTime() - last_time) >= self.repeat_time
            ):
                if self.is_windows:
                    current_sound.play()
                else:
                    temp_sound = sound.Sound(
                        self.sounds_dict[sound_names[current_index]],
                        volume=current_volume,
                    )
                    temp_sound.play()
                last_time = self.clock.getTime()

            core.wait(0.01)  # Short wait to reduce CPU usage

        win.close()
        return slider_vol

    def play_adjusted_sounds(self, adjusted_volumes: Dict[str, float]) -> None:
        # Play sounds with adjusted volumes
        for sound_name, volume in adjusted_volumes.items():
            if self.is_windows:
                self.sounds_dict[sound_name].setVolume(volume)
                self.sounds_dict[sound_name].play()
            else:
                temp_sound = sound.Sound(self.sounds_dict[sound_name], volume=volume)
                temp_sound.play()
            core.wait(1)  # Wait to ensure sound playback is heard


def main():
    # Define the sound files to be used
    sound_files = [f"tone_{i}.wav" for i in range(4)]
    reference_sound_file = "tone_13.wav"

    # Initialize the VolumeAdjuster with the specified parameters
    adjuster = VolumeAdjuster(
        sound_files,
        reference_sound_file,
        sound_dir="tones",
        increment_rate=0.005,
        repeat_rate=1.0,
        start_value=0.1,
        reference_sound_volume=0.1,
        slider_style="slider",
    )

    # Adjust volumes and store the results
    adjusted_volumes = adjuster.adjust_volume()
    adjuster.play_adjusted_sounds(adjusted_volumes)
    print("Adjusted volumes:", adjusted_volumes)


if __name__ == "__main__":
    main()
