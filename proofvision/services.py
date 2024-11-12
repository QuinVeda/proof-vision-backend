from django.conf import settings
import boto3
import json

import io
import librosa
import numpy as np
import soundfile as sf
from moviepy.editor import VideoFileClip, AudioFileClip
from tensorflow.keras.models import load_model


class AmazonLambdaService:
    AWS_LAMBDA_REGION_NAME = settings.AWS_LAMBDA_REGION_NAME
    AWS_LAMBDA_FUNCTION_NAME = settings.AWS_LAMBDA_FUNCTION_NAME

    def __init__(self):
        self.client = boto3.client("lambda", region_name=self.AWS_LAMBDA_REGION_NAME)

    def start(self, data):
        self.client.invoke(
            FunctionName=self.AWS_LAMBDA_FUNCTION_NAME,
            InvocationType="Event",
            Payload=json.dumps(data),
        )


class PredictionService:
    def __init__(self):
        self.model_path = "static/model.keras"

    def extract_frame_features(self, file_path, frame_duration=1.0):
        file_path = file_path[1:]
        if ".mp4" in file_path:
            video_clip = VideoFileClip(file_path)
            audio = video_clip.audio
        else:
            audio = AudioFileClip(file_path)
        fps = audio.fps
        audio_samples = np.array(
            list(audio.iter_frames(fps=fps, dtype="float32"))
        ).flatten()
        buffer = io.BytesIO()
        sf.write(buffer, audio_samples, fps, format="wav")
        buffer.seek(0)
        x, sr = librosa.load(buffer, sr=None)

        # Split audio into frames of 'frame_duration' seconds
        frame_length = int(frame_duration * sr)
        frames = []
        timestamps = []

        for i in range(0, len(x), frame_length):
            if i + frame_length <= len(x):
                # Extract MFCCs for each frame and store the timestamp
                frame_mfcc = librosa.feature.mfcc(
                    y=x[i : i + frame_length], sr=sr, n_mfcc=20
                )
                frames.append(frame_mfcc)
                timestamp = i / sr  # Convert index to seconds
                timestamps.append(timestamp)

        return frames, timestamps

    def predict(self, file_path, frame_duration=1.0):
        # Load the trained model
        model = load_model(self.model_path)

        # Extract features and timestamps for each frame in the new video
        frames, timestamps = self.extract_frame_features(file_path, frame_duration)

        if frames is None or timestamps is None:
            return None

        # Reshape frames for model input
        frames = np.array(frames)[..., np.newaxis]

        # Predict on each frame
        predictions = model.predict(frames)
        frames = np.argmax(predictions, axis=1)
        real_confidance = []
        fake_confidance = []
        for pred in predictions:
            real_confidance.append(float(pred[0]))
            fake_confidance.append(float(pred[1]))
        authenticity = float(np.mean(real_confidance))
        fakeness = float(np.mean(fake_confidance))
        frames = [int(frame) for frame in frames]

        data = {
            "real_confidance": real_confidance,
            "fake_confidance": fake_confidance,
            "authenticity": authenticity,
            "fakeness": fakeness,
            "frames": list(frames),
            "is_real": True if authenticity > fakeness else False,
        }
        return data
