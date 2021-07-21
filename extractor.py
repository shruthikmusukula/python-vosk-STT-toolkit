#!/usr/bin/env python3

from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from vosk import Model, KaldiRecognizer, SetLogLevel

import datetime
import json
import os
import srt
import subprocess

MODEL_PATH = "data/model"
SAMPLE_RATE = 16000
WORDS_PER_LINE = 7

class VOSK_Extractor:
    def __init__(self, file, sampleRate=None, model=None):
        self.check_for_model()

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
        self.rec = KaldiRecognizer(self.model, self.sampleRate)
        self.rec.SetWords(True) # Important for SRT file construction

        # Initialize SRT Variables
        self.output = ""
        self.results = []
        self.subs = []

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
        output = json.loads(self.output)
        print("Result from [" + self.dataFile + "]: " + output["text"] + "\n")

    def process_input_file(self):
        # Call to initialize subprocess with VOSK API
        self.initialize_process()

        # Preprocessing of detected speech
        while True:
            data = self.process.stdout.read(4000)
            if len(data) == 0:
                break
            if self.rec.AcceptWaveform(data):
                self.results.append(self.rec.Result())

        # Save extracted output
        self.output = self.rec.FinalResult()

        # Add extracted text to results
        self.results.append(self.output)

        # Call to prepare result
        self.prepare_result()

    def built_srt(self):
        # Build SRT File content
        for i, res in enumerate(self.results):
            jres = json.loads(res)
            if not 'result' in jres:
                continue
            words = jres['result']
            for j in range(0, len(words), WORDS_PER_LINE):
                line = words[j: j + WORDS_PER_LINE]
                s = srt.Subtitle(index=len(self.subs),
                                 content=" ".join([l['word'] for l in line]),
                                 start=datetime.timedelta(seconds=line[0]['start']),
                                 end=datetime.timedelta(seconds=line[-1]['end']))
                self.subs.append(s)
        self.write_to_srt_file()

    def write_to_srt_file(self):
        file = open("output.srt", "w+")
        file.write(srt.compose(self.subs))

    def embed_subtitles(self):
        generator = lambda txt: TextClip(txt, font = 'Lexend', fontsize = 16, color = 'white')
        subtitles = SubtitlesClip("output.srt", generator)

        video = VideoFileClip(self.dataFile)
        result = CompositeVideoClip([video, subtitles.set_pos(('center', 'bottom'))])

        result.write_videofile("subtitle_output.mp4", fps = video.fps,
                                temp_audiofile = "temp-audio.m4a", remove_temp = True, codec = "libx264", audio_codec = "aac")


# Lone Executable Command (If Main Was In Here): python3 extractor.py data/test.mp4
