#!/usr/bin/env python3

from vosk import Model, KaldiRecognizer, SetLogLevel
import sys
import os
import wave
import subprocess

class VOSK_Extractor:
    def __init__(self, SAMPLE_RATE=None, model=None):
        if SAMPLE_RATE is None:
            self.SAMPLE_RATE = 16000
        else:
            self.SAMPLE_RATE = SAMPLE_RATE

        if model is None:
            self.model = Model("data/model")
        else:
            self.model = Model(model)

        # VOSK Model Setup
        SetLogLevel(0)
        self.check_for_model()
        self.rec = KaldiRecognizer(self.model, self.SAMPLE_RATE)

    def check_for_model(self):
        if not os.path.exists("data/model"):
            print(
                "Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder."
                "This is the training model needed to work with the VOSK API.")
            exit(1)

    def process_ffmpeg(self):
        process = subprocess.Popen(['ffmpeg', '-loglevel', 'quiet', '-i',
                                    sys.argv[1],
                                    '-ar', str(self.SAMPLE_RATE) , '-ac', '1', '-f', 's16le', '-'],
                                    stdout=subprocess.PIPE)
        while True:
            data = process.stdout.read(4000)
            if len(data) == 0:
                break
            if self.rec.AcceptWaveform(data):
                print(self.rec.Result())
            else:
                print(self.rec.PartialResult())
        print(self.rec.FinalResult())


if __name__ == "__main__":
    extractor = VOSK_Extractor()
    extractor.process_ffmpeg()

# Executable: python3 process_ffmpeg.py data/test.mp4
