import base64
import struct
import wave
from threading import Thread

import pyaudio
import pydub
from robot.api import logger
from robot.api.deco import keyword
from robot.api.logger import console

class Error(Exception):
    """Represents an error in the Audio."""


class Audio:
    """This library provides keywords to record, play and convert Audio.

    == Play Audio

    The following keyword sequence can be used to play audio from a file.

    | Audio Set Output Device | 1             |
    | Audio Play              | test_tone.wav |

    The `Audio Set Output Device` specifies the index out the sound card to
    be used for playing audio. Since a system can have more than one output
    device it is necessary to select a specific output device.

    The following keyword sequence can be used to record audio to a file.

    | Audio Set Input Device  | 1             |
    | Audio Start Recording   |
    | Audio Stop Recording    | test_tone.wav |

    The `Audio Set Input Device` specifies the index out the sound card to
    be used for recording audio.
    """

    def __init__(self):
        self.record_th = None
        self.stop = True
        self.stream = None
        self.pyaudio = pyaudio.PyAudio()
        self.format = pyaudio.paInt16
        self.channels = 1
        self.chunk = 1024
        self.rate = 44100
        self.input_device = -1
        self.output_device = -1
        self.save_data = []


    def _log_devices_list(self):
        device_count = self.pyaudio.get_device_count()
        for i in range(0, device_count):
            info = self.pyaudio.get_device_info_by_index(i)
            logger.write("Device {} = {}".format(info["index"], info["name"]))

    @keyword("Audio Set Input Device")
    def set_input_device(self, device: int) -> None:
        """Sets the input audio device index.

        Check the Robot log for available devices and their index in the current
        system.
        """
        self._log_devices_list()
        info = self.pyaudio.get_device_info_by_index(device)
        logger.write(f"Selected Input Device: {info}")
        self.input_device = device

    @keyword("Audio Set Output Device")
    def set_output_device(self, device: int) -> None:
        """Sets the output audio device index.

        Check the Robot log for available devices and their index in the current
        system.
        """
        self._log_devices_list()
        info = self.pyaudio.get_device_info_by_index(device)
        logger.write(f"Selected Output Device: {info}")
        self.output_device = device

    def _start(self) -> None:
        """
        Record audio until calling Stop Record Method.
        """
        logger.write("Recording Started")
        self.stop = False
        while not self.stop:
            data = self.stream.read(self.chunk)
            self.save_data.append(data)

    def _save_audio_file(self, audiofile: str) -> None:
        """
        Convert the given list to numpy array and store it to Audiofile.
        """
        with wave.open(audiofile, "wb") as wfile:
            wfile.setnchannels(self.channels)
            wfile.setsampwidth(self.pyaudio.get_sample_size(self.format))
            wfile.setframerate(self.rate)
            wfile.writeframes(b''.join(self.save_data))

        logger.write(f"DTMF Tone Saved: {audiofile}")

    @staticmethod
    def _log_audio_file(audiofile: str) -> None:
        """
        Convert the audio file in HTML format and log the converted file in report file.
        """
        with open(audiofile, 'rb') as f_point:
            b64_fbuffer = base64.b64encode(f_point.read())
        html_player = f'<audio controls src="data:audio/wav;base64,{b64_fbuffer.decode()}"></audio>'
        logger.write(html_player, html=True)

    @keyword("Audio Convert format WAV to MP3")
    def convert_audio_format(self, input_file: str, output_file: str) -> None:
        """Converts audio file from .WAV format to .MP3 format.

       ``input_file`` specified .WAV file path. ``output_file`` specifies .MP3
       file path.
        """
        pydub.AudioSegment.from_wav(input_file).export(output_file, format='mp3')

    @keyword("Audio Start Recording")
    def start_record(self) -> None:
        """Starts recording audio from the selected microphone.

        *Example*

        | Audio Start Recording |
        """
        self.stream = self.pyaudio.open(format=self.format,
                                        channels=self.channels,
                                        rate=self.rate,
                                        frames_per_buffer=self.chunk,
                                        input_device_index=self.input_device,
                                        input=True,
                                        output=False)
        self.record_th = Thread(target=self._start)
        self.record_th.start()
        logger.write("Recording Started")

    @keyword("Audio Stop Recording")
    def stop_record(self, audiofile: str) -> None:
        """Stops recording.

        This method stops recording started with `Start Recording`. The
        `audiofile` specifies the path where the recorded audio will be stored
        in .WAV file format. The recorded audio is also logged to the Robot log
        file.

        *Example*

        | Audio Stop Recording    | test_tone.wav |

        """
        self.stop = True
        try:
            self.record_th.join()
        except AttributeError as error:
            raise Error("Initiate Recorder") from error
        logger.write("Recording Stopped")
        self._save_audio_file(audiofile)
        self._log_audio_file(audiofile)

    @keyword("Audio Play File")
    def play(self, audiofile: str):
        chunk = 1024
        with wave.open(audiofile, 'rb') as wfile:
            format = self.pyaudio.get_format_from_width(wfile.getsampwidth())
            stream = self.pyaudio.open(format = format,
                                       channels = wfile.getnchannels(),
                                       rate = wfile.getframerate(),
                                       output = True)

            data = wfile.readframes(chunk)
            while data != b'':
                stream.write(data)
                data = wfile.readframes(chunk)

            stream.close()
