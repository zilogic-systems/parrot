"""
Keyword Library Provides API to process DTMF utility.
"""
import base64
import itertools
import struct

import numpy as np
import pydub
import pydub.silence
from robot.api import logger
from robot.api.deco import keyword
from robot.api.logger import console


class Error(Exception):
    """Represents an error in the DTMF."""


class DTMF:
    """A library providing keywords to decode and generate DTMF tones.

    A tone is signal with one frequency. DTMF represent numbers a combination of
    two tones. DTMF sequences are easy to generate and detect. This makes it
    suitable for audio related testing. This library provides keywords to
    convert a string of digits into DTMF tones and can convert a DTMF sequence
    into string of digits.

    This library provides keywords for

        - Generating DTMF Tone with the given sequence.
        - Verifying the Recorded tone with DTMF Tone.

    *Example*

    | DTMF Generator    | 1243 | test_tone.wav | 5 | 5 | 0.25 | 0.25 |
    | Verify DTMF Tone  | 1243 | test_tone.mp3 |
    """

    ROBOT_AUTO_KEYWORDS = False
    ROBOT_LIBRARY_SCOPE = 'TEST'

    def __init__(self) -> None:
        self.stream = []
        self.keymap = [
            ['0', 941, 1336], ['*', 941, 1209], ['#', 941, 1477],
            ['1', 697, 1209], ['2', 697, 1336], ['3', 697, 1477],
            ['4', 770, 1209], ['5', 770, 1336], ['6', 770, 1477],
            ['7', 852, 1209], ['8', 852, 1336], ['9', 852, 1477],
            ['A', 697, 1633], ['B', 770, 1633], ['C', 852, 1633],
            ['D', 941, 1633]]

    @staticmethod
    def _log_audio_file(audiofile: str) -> bool:
        """
        Convert the audio file in HTML format and log the converted file in report file.
        """
        with open(audiofile, 'rb') as f_point:
            b64_fbuffer = base64.b64encode(f_point.read())
        html_player = f'<audio controls src="data:audio/wav;base64,{b64_fbuffer.decode()}"></audio>'
        logger.write(html_player, html=True)
        return True

    def _find_nearest(self, freq_1: np.float64, freq_2: np.float64, min_dist: int) -> tuple:
        """
        Finding Nearest Frequency in the Keymap.
        """
        answer = ''
        for key in self.keymap:
            dist1 = np.abs(freq_1 - key[1]) + np.abs(freq_2 - key[2])
            dist2 = np.abs(freq_1 - key[2]) + np.abs(freq_2 - key[1])
            dist = np.min([dist1, dist2])
            if dist < min_dist:
                min_dist = dist
                answer = key[0]
        return answer, min_dist

    def _process_tone(self, signal: list, rate: int) -> str:
        """
        Process the signal with sample rate.

            - ``signal``: audiodata.
            - ``rate``: samplerate
        """
        result = ''

        dtft = np.fft.fft(signal)[range(int(len(signal)/2))]
        dtft_abs = np.abs(dtft)
        high_amp = np.sort(dtft_abs)[-7:]

        high_f = np.array([])
        for freq in high_amp:
            high_f = np.append(high_f, np.where(dtft_abs == freq)[0])

        if high_f.shape[0] != 7:
            return ''

        sec = rate / len(signal)
        high_f = np.array(high_f) * sec

        logger.write("{}".format(high_f))

        min_dist = 15
        for freq_1, freq_2 in itertools.combinations(high_f, 2):
            result_temp, dist = self._find_nearest(freq_1, freq_2, min_dist)
            if dist < min_dist:
                min_dist = dist
                result = result_temp

        return result

    @keyword("Verify DTMF Tone")
    def verify_dtmf_seq(self, expected_sequence: str, audiofile: str) -> None:
        """Verifies the recorded tone with the expected sequence.

        Decodes the DTMF sequence in the ``audiofile`` and verifies if it
        matches the expected sequence specified by ``expected_sequence``. Fails
        if the decoded sequence does not match the expected sequence.

        *Example*

        | Verify DTMF Tone    | 1243 | test_tone.wav | 5 | 5 | 0.25 | 0.25 |
        """
        expected_sequence = list(expected_sequence)

        sound = pydub.AudioSegment.from_file(audiofile)
        rate = sound.frame_rate
        logger.write(rate)

        if sound.sample_width == 1:
            np_data_type = np.int8
        elif sound.sample_width == 2:
            np_data_type = np.int16
        elif sound.sample_width == 4:
            np_data_type = np.int32
        else:
            raise Error("unsupported audio sample width")

        logger.write(np_data_type)

        tone_segs = pydub.silence.split_on_silence(sound, min_silence_len=10)
        logger.write(tone_segs)
        logger.write(len(tone_segs))

        buffer = []
        next_index = 0

        for seg in tone_segs:
            data = np.frombuffer(seg.raw_data, dtype=np_data_type)
            logger.write("{}".format(data))
            try:
                key = self._process_tone(data, rate)
                logger.write(key)
            except Error:
                # if no data from wav will break the loop
                break

            if key:
                logger.write(f"Detected:{key=}")
                # If we've detected a DTMF tone, add it to the buffer
                buffer.append(key)

                # If the buffer contains the next expected tone, move to the next index
                try:
                    if buffer[next_index] == expected_sequence[next_index]:
                        next_index += 1
                except IndexError as error:
                    raise Error(error) from error

        captured = ' '.join(buffer)
        logger.write(f"Captured Sequence: {captured}")
        logger.write(f"Expected Sequence: {' '.join(expected_sequence)}")
        if buffer == expected_sequence:
            logger.write("DTMF Tone Verification Succeed")
            console(f"Verified DTMF Tone {captured}")
            return
        raise Error("Failed to Verify DTMF Tone")

    def _dtmf_encoder(self, num: str, sam_freq: int, tone_duration: float) -> np.ndarray:
        """
        Encoding the Given Number to dtmf data

        *Returns*

        	``numpy.ndarray``: For given number.
        """
        time_tone = np.arange(0, int(tone_duration*sam_freq))
        for data in self.keymap:
            if data[0] == num:
                low_freq = data[1]
                high_freq = data[2]
        low_pitch = np.sin(2*np.pi*(low_freq/sam_freq)*time_tone)
        high_pitch = np.sin(2*np.pi*(high_freq/sam_freq)*time_tone)
        dtmf_tone = low_pitch + high_pitch

        return dtmf_tone

    @staticmethod
    def _audio_delay(delay_time: float, sam_freq: int) -> np.ndarray:
        """
        Generate numpy array for audio delay for the given time.

        *Returns*

            ``np.ndarray``: For delay tone.
        """
        delay_tone = np.zeros(int(delay_time*sam_freq))
        return delay_tone

    @staticmethod
    def _add_wav_header(sample_rate, audio) -> bytes:
        """
        Adding wave file header to the raw data.

            - ``sample_rate``: Sample Rate of the wave file.
            - ``audio``: Audio Data.

        Returns:
            ``bytes``: Wave file data in bytes format.
        """
        audio = audio.astype(np.float32)
        audio = audio.tostring()
        if audio.startswith("RIFF".encode()):
            return audio
        sample_num = len(audio)
        header_info = "RIFF".encode()
        header_info += struct.pack('i', sample_num + 44)
        header_info += 'WAVEfmt '.encode()
        header_info += struct.pack('i', 16)
        header_info += struct.pack('h', 1)
        header_info += struct.pack('h', 1)
        header_info += struct.pack('i', sample_rate)
        header_info += struct.pack('i', sample_rate * int(32 / 8))
        header_info += struct.pack("h", int(32 / 8))
        header_info += struct.pack("h", 32)
        header_info += "data".encode()
        header_info += struct.pack('i', sample_num)
        audio = header_info + audio
        return audio

    @keyword("DTMF Generator")
    def dtmf_generator(self,
                       expected: str,
                       audiofile: str,
                       start_padding: int = 0,
                       end_padding: int = 0,
                       tone_duration:float = 0.25,
                       spacing: float = 0.25
                       ) -> None:
        """Generates a DTMF sequence.

        This method generates the DTMF sequence, for the string of digits
        specified as ``expected``. The resulting audio data is stored in the file
        ``audiofile`` in a wav format. The ``start_padding`` specifies the delay in seconds
        from the start of the audio that the DTMF sequence is to be generated. The
        ``end_padding`` specifies the delay at the end of the audio file in seconds. The
        ``spacing`` specifies the space between each tones. The ``tone_duration``
        specifies the time for each audio tones.

        *Example*

        | DTMF Generator    | 1243 | test_tone.wav | 5 | 5 | 0.25 | 0.25 |
        """
        sam_freq = 16000
        total_duration = start_padding + end_padding + (tone_duration + spacing)*len(expected)
        audio = np.array([])
        delay_tone = self._audio_delay(start_padding, sam_freq)
        total_duration -= start_padding
        audio = np.concatenate((audio, delay_tone))
        for num in expected:
            dtmf_tone = self._dtmf_encoder(num, sam_freq, tone_duration)
            total_duration -= tone_duration
            delay_tone = self._audio_delay(spacing, sam_freq)
            total_duration -= spacing
            audio = np.concatenate((audio, delay_tone, dtmf_tone))

        if total_duration:
            delay_tone = self._audio_delay(total_duration, sam_freq)
            audio = np.concatenate((audio, delay_tone))
        audio = self._add_wav_header(16000, audio)
        with open(audiofile, 'wb') as f_point:
            f_point.write(audio)
        self._log_audio_file(audiofile)
        return
