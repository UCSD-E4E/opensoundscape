import pytest
from pathlib import Path
import numpy as np
import pandas as pd
from opensoundscape.audio import Audio
from numpy.testing import assert_allclose
from opensoundscape.preprocess import actions
from opensoundscape.preprocess.preprocessors import (
    CnnPreprocessor,
    AudioLoadingPreprocessor,
    PreprocessingError,
)
from PIL import Image


@pytest.fixture()
def dataset_df():
    paths = ["tests/audio/silence_10s.mp3", "tests/audio/veryshort.wav"]
    labels = [[0, 1], [1, 0]]
    return pd.DataFrame(index=paths, data=labels, columns=[0, 1])


@pytest.fixture()
def overlay_df():
    paths = ["tests/audio/great_plains_toad.wav"]
    labels = [[1, 0]]
    return pd.DataFrame(index=paths, data=labels, columns=[0, 1])


def test_audio_loading_preprocessor(dataset_df):
    """should retain original sample rate"""
    dataset = AudioLoadingPreprocessor(dataset_df)
    assert dataset[0]["X"].samples.shape == (44100 * 10,)


def test_audio_resample(dataset_df):
    """should retain original sample rate"""
    dataset = AudioLoadingPreprocessor(dataset_df)
    dataset.actions.load_audio.set(sample_rate=16000)
    assert dataset[0]["X"].samples.shape == (16000 * 10,)


def test_cnn_preprocessor(dataset_df):
    """should return tensor and labels"""
    dataset = CnnPreprocessor(dataset_df)
    dataset.augmentation_off()
    sample1 = dataset[0]["X"]
    assert sample1.numpy().shape == (3, 224, 224)
    assert dataset[0]["y"].numpy().shape == (2,)


def test_cnn_preprocessor_augment_off(dataset_df):
    """should return same image each time"""
    dataset = CnnPreprocessor(dataset_df)
    dataset.augmentation_off()
    sample1 = dataset[0]["X"].numpy()
    sample2 = dataset[0]["X"].numpy()
    assert np.array_equal(sample1, sample2)


def test_cnn_preprocessor_augent_on(dataset_df):
    """should return different images each time"""
    dataset = CnnPreprocessor(dataset_df)
    sample1 = dataset[0]["X"]
    sample2 = dataset[0]["X"]
    assert not np.array_equal(sample1, sample2)


def test_cnn_preprocessor_overlay(dataset_df, overlay_df):
    """should return different images each time"""
    dataset = CnnPreprocessor(dataset_df, overlay_df=overlay_df)
    sample1 = dataset[0]["X"]
    dataset.actions.overlay.off()
    sample2 = dataset[0]["X"]
    assert not np.array_equal(sample1, sample2)


def test_overlay_update_labels(dataset_df, overlay_df):
    """should return different images each time"""
    dataset = CnnPreprocessor(dataset_df, overlay_df=overlay_df)
    dataset.actions.overlay.set(update_labels=True)
    print(dataset[0]["y"])
    assert np.array_equal(dataset[0]["y"].numpy(), [1, 1])


def test_cnn_preprocessor_fails_on_short_file(dataset_df):
    """should fail on short file when audio duration is specified"""
    dataset = CnnPreprocessor(dataset_df, audio_length=5.0)
    with pytest.raises(PreprocessingError):
        sample = dataset[1]["X"]