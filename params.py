import midi_processor.processor as sequence
import os # max_seq = 2048
max_seq=2048
l_r = 0.001
embedding_dim = 256
num_attention_layer = 6
batch_size = 10
loss_type = 'categorical_crossentropy'
event_dim = sequence.RANGE_NOTE_ON + sequence.RANGE_NOTE_OFF + sequence.RANGE_TIME_SHIFT + sequence.RANGE_VEL
pad_token = event_dim
token_sos = event_dim + 1
token_eos = event_dim + 2
vocab_size = event_dim + 3

def get_current_datetime():
    from datetime import datetime
    now = datetime.now()
    dt_name = now.strftime("%m_%d_%Y__%H_%M_%S")
    return dt_name

try:
    import google.colab

    IS_ON_GOOGLE_COLAB = True
except:
    IS_ON_GOOGLE_COLAB = False

if IS_ON_GOOGLE_COLAB:
    from google.colab import drive
    FOLDER_ROOT = "/content/drive/MyDrive/magisterka/SheetMusicGenerator2"
else:
    FOLDER_ROOT = "."

TEST_RUN = True
NORMALIZE_NOTES = True
USE_COMPUTED_VALUES = True
USE_SAVE_POINT = False

# NORMALIZATION_BOUNDARIES = [3, 4]
# EPOCHS = 1000
# LATENT_VECTOR_DIM = 2
# BATCH_SIZE = 256
# SEQUENCE_LENGTH = 32

FOLDER_ROOT = "."
# COMPUTED_INT_TO_NOTE_PATH = "/content/drive/MyDrive/magisterka/SheetMusicGenerator2/AUTOENCODER/data/dicts/int_to_note_08_19_2021__17_25_44"
# COMPUTED_INT_TO_DURATION_PATH = "/content/drive/MyDrive/magisterka/SheetMusicGenerator2/AUTOENCODER/data/dicts/int_to_duration_08_19_2021__17_25_44"
# COMPUTED_NOTES_PATH = "/content/drive/MyDrive/magisterka/SheetMusicGenerator2/AUTOENCODER/data/notes/notes_08_19_2021__17_25_44"
# COMPUTED_DURATIONS_PATH = "/content/drive/MyDrive/magisterka/SheetMusicGenerator2/AUTOENCODER/data/durations/durations_08_19_2021__17_25_44"
COMPUTED_DATA_PATH = "AUTOENCODER/data/data_file_12_06_2021__19_53_42"

SAVE_POINT = "AUTOENCODER/checkpoints/08_19_2021__18_34_10/epoch=014-loss=383.5284-acc=0.0000.hdf5"
AUTOENCODER = "AUTOENCODER"
TRANSFORMER = "TRANSFORMER"

MODEL_NAME = TRANSFORMER
MODEL_FOLDER_ROOT = os.path.join(FOLDER_ROOT, MODEL_NAME)
CURR_DT = get_current_datetime()
MODEL_DIR_PATH = os.path.join(MODEL_FOLDER_ROOT, "generated_models")
OCCURENCES = os.path.join(MODEL_FOLDER_ROOT, "data", "occurences")

DATA_DIR = os.path.join(MODEL_FOLDER_ROOT, "data")
DATA_NOTES_DIR = os.path.join(DATA_DIR, "notes")
DATA_DURATIONS_DIR = os.path.join(DATA_DIR, "durations")

DATA_FILE_PATH = os.path.join(DATA_DIR, "data_file_" + str(CURR_DT))

DATA_DICTS_DIR = os.path.join(DATA_DIR, "dicts")
DATA_INT_TO_NOTE_PATH = os.path.join(DATA_DICTS_DIR, "int_to_note_" + str(CURR_DT))
DATA_INT_TO_DURATION_PATH = os.path.join(DATA_DICTS_DIR, "int_to_duration_" + str(CURR_DT))
DATA_NOTES_PATH = os.path.join(DATA_NOTES_DIR, "notes_" + str(CURR_DT))

DATA_DURATIONS_PATH = os.path.join(DATA_DURATIONS_DIR, "durations_" + str(CURR_DT))
# MIDI_SONGS_DIR = os.path.join(FOLDER_ROOT, "midi_songs")
MIDI_SONGS_DIR = os.path.join(FOLDER_ROOT, "midi_songs_smaller")
# MIDI_SONGS_DIR = os.path.join(FOLDER_ROOT, "midi_songs_medium")
MIDI_GENERATED_DIR = os.path.join(MODEL_FOLDER_ROOT, "midi_generated")
MIDI_SONGS_REGEX = os.path.join(MIDI_SONGS_DIR, "*.mid")
CHECKPOINTS_DIR = os.path.join(MODEL_FOLDER_ROOT, "checkpoints")
CHECKPOINT = os.path.join(CHECKPOINTS_DIR, str(CURR_DT))
LOGS_DIR = os.path.join(MODEL_FOLDER_ROOT, "logs")

LOG = os.path.join(LOGS_DIR, str(CURR_DT))
all_paths = [MODEL_DIR_PATH, OCCURENCES, DATA_NOTES_DIR, DATA_DURATIONS_DIR, DATA_DICTS_DIR,
             MIDI_GENERATED_DIR, CHECKPOINTS_DIR, CHECKPOINT, LOGS_DIR, LOG]
