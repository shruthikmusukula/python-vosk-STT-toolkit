#!/usr/bin/env python3

from vosk import Model, KaldiRecognizer, SetLogLevel
import os
import json
import subprocess

SAMPLE_RATE = 16000
MODEL_PATH = "data/model"

class VOSK_Extractor:
    def __init__(self, file, sampleRate=None, model=None):
        self.dataFile = file

        if sampleRate is None:
            self.sampleRate = SAMPLE_RATE
        else:
            self.sampleRate = sampleRate

        if model is None:
            self.model = Model(MODEL_PATH)
        else:
            self.model = Model(model)

        # VOSK General Model Setup
        SetLogLevel(0)
        self.check_for_model()
        self.rec = KaldiRecognizer(self.model, self.sampleRate)

    def check_for_model(self):
        if not os.path.exists("data/model"):
            print(
                "Please download a valid model from https://alphacephei.com/vosk/models and "
                "unpack as 'any_name' in your working directory. This is the training model "
                "needed to work with the VOSK API.")
            exit(1)

    def initialize_process(self):
        self.process = subprocess.Popen(['ffmpeg', '-loglevel', 'quiet', '-i', self.dataFile, '-ar',
                                    str(self.sampleRate) , '-ac', '1', '-f', 's16le', '-'],
                                    stdout=subprocess.PIPE)

    def prepare_result(self):
        # Load string into JSON format and extract resulting text
        result = json.loads(self.rec.FinalResult())
        print("Result from [" + self.dataFile + "]: " + result["text"])

    def process_ffmpeg(self):
        # Call to initialize subprocess with VOSK API
        self.initialize_process()

        # Preprocessing of detected speech
        while True:
            data = self.process.stdout.read(4000)
            if len(data) == 0:
                break
            if self.rec.AcceptWaveform(data):
                self.rec.Result()

        # Call to prepare result
        self.prepare_result()

# Lone Executable Command (If Main Was In Here): python3 extractor.py data/test.mp4
