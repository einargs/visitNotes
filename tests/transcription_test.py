import sys
import struct
sys.path[0] = '/Users/wesleymitchell/TNHIMS/wesFork/visitNotes/'
print(sys.path[0])
from transcription import AudioTranscriber
import wave

audio_path = "../katiesteve.wav"

data = wave.open(audio_path)

transcrib = AudioTranscriber(input_stream=data)
transcrib.push_stream.write(data.readframes(100000))
transcrib.push_stream.close()
transcrib.transcribe_from_file()
