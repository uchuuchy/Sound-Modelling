import ffmpeg

class CleanUp:
    def __init__(self, stream: str):
        self._stream = stream

    def convert(self):
        if str(self._stream.split(".", 1)[1].upper()) == "MP3":
            (
                ffmpeg
                .input(self._stream)
                .output(self._stream.replace(".mp3", ".wav"), ac=1)
                .run(overwrite_output=True, quiet=True)
            )
            return self._stream.replace(".mp3", ".wav")
        elif str(self._stream.split(".", 1)[1].upper()) == "WAV":
            (
                ffmpeg
                .input(self._stream)
                .output(self._stream, ac=1)
                .run(overwrite_output=True, quiet=True)
            )
            return self._stream
