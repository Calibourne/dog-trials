from dotenv import load_dotenv
import os
load_dotenv()
dog_names = os.getenv("DOG_NAMES").split(",")
test_structure = os.getenv("TEST_STRUCTURE").split(",")
num_of_trials = int(os.getenv("NUM_OF_TRIALS"))