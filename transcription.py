import azure.cognitiveservices.speech as speechsdk
import dotenv
import os
import time 

dotenv.load_dotenv()

class AudioTranscriber():
    def __init__(self, input_file=None, input_stream=None, output_filename=None):
        
        self.input_file = input_file
        self.input_stream = input_stream
        
        # requires azure api key
        self.speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'),
                                                    region=os.environ.get('SPEECH_REGION'))

        # just english for now
        self.speech_config.speech_recognition_language = 'en-US'
        
        # determine input type
        # input from file is primarily for debugging 
        if self.input_file != None:
            self.audio_config = speechsdk.AudioConfig(filename=self.input_file)
        elif self.input_stream != None:
            audio_format = speechsdk.audio.AudioStreamFormat()
            self.push_stream = speechsdk.audio.PushAudioInputStream(audio_format)
            self.audio_config = speechsdk.AudioConfig(stream=self.push_stream)
        
        self.transcriber = speechsdk.transcription.ConversationTranscriber(audio_config=self.audio_config, 
                                                                           speech_config=self.speech_config)

        self.transcriber.transcribed.connect(self.conversation_transcriber_transcribed_cb)
        self.transcriber.session_started.connect(self.conversation_transcriber_session_started_cb)
        self.transcriber.session_stopped.connect(self.conversation_transcriber_session_stopped_cb)
        self.transcriber.canceled.connect(self.conversation_transcriber_recognition_canceled_cb)

        self.transcriber.session_stopped.connect(self.stop_cb)
        self.transcriber.canceled.connect(self.stop_cb)


        self.transcribing_stop = False

        self.buffer = ""

        self.output_filename = output_filename

    def conversation_transcriber_session_stopped_cb(self, evt: speechsdk.SessionEventArgs):
        self.buffer += "[Session Ended]\n"

    def conversation_transcriber_recognition_canceled_cb(self, evt: speechsdk.SessionEventArgs):
        self.buffer += "[Transcription Canceled]\n"

    def conversation_transcriber_session_started_cb(self, evt: speechsdk.SessionEventArgs):
        self.buffer += "[Conversation Started]\n"
    
    def conversation_transcriber_transcribed_cb(self, evt: speechsdk.SpeechRecognitionEventArgs):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            speaker = evt.result.speaker_id
            text = evt.result.text
            line = f"[{speaker}] {text} \n"
            self.buffer += line
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            self.buffer += "[Unable to Transcribe]"
    def stop_cb(self, evt: speechsdk.SessionEventArgs):
        self.buffer += "[Stopping]"
        self.transcribing_stop = True

    def transcribe_from_file(self):
        self.transcriber.start_transcribing_async()
        
        while not self.transcribing_stop:
            time.sleep(2)
        self.transcriber.stop_transcribing_async()

    def flush_buffer(self):
        if(self.output_filename):
            try: 
                with open(self.output_filename, 'a') as file_obj:
                    file_obj.write(self.buffer)
                    file_obj.close()

            except:
                print("Error occured writing to file")


        else:
            print(self.buffer)

        self.buffer = "" 

        
if __name__ == "__main__":
    transcriber_service = AudioTranscriber(input_file="M_0398_12y5m_1.wav")
    transcriber_service.transcribe_from_file()
    print(transcriber_service.buffer)
