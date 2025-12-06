# Install dependencies (if needed)
# !pip install tensorflow numpy matplotlib waymo-open-dataset-tf-2-12-0==1.6.7

# Import Libraries
import pandas as pd
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import os

# Import Waymo dataset libraries
from waymo_open_dataset.protos import end_to_end_driving_data_pb2 as wod_e2ed_pb2

# Set plotting style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 8)

print("✅ Libraries imported successfully!")

from google.colab import drive
drive.mount('/content/drive')

# Configure dataset path
TFRECORD_FILE = '/content/drive/MyDrive/ECE143_Datasets/training_202504031202_202504151040.tfrecord-00000-of-00263'
NUM_SAMPLES = 1000  # Analyze first 100 samples

# Load TFRecord dataset
dataset = tf.data.TFRecordDataset(TFRECORD_FILE, compression_type='')

def analyze_driving_behavior(data):
    """
    Analyzes driving behavior using vector projection + Intent + Jerk.
    Context: American Urban/Highway (m/s and m/s^2).
    """
    if not hasattr(data, 'past_states') or len(data.past_states.pos_x) == 0:
        return None

    # --- 1. EXTRACT RAW DATA ---
    pos_x = np.array(data.past_states.pos_x)
    pos_y = np.array(data.past_states.pos_y)
    vel_x = np.array(data.past_states.vel_x)
    vel_y = np.array(data.past_states.vel_y)
    accel_x = np.array(data.past_states.accel_x)
    accel_y = np.array(data.past_states.accel_y)
    ego_intent = data.intent

    if len(vel_x) < 2: return None

    # --- 2. CALCULATE ACCELERATION VECTORS ---
    speeds = np.sqrt(vel_x**2 + vel_y**2)
    moving_mask = speeds > 1.0

    long_accels = np.zeros_like(speeds) # Gas/Brake
    lat_accels  = np.zeros_like(speeds) # Swerve Force

    if np.any(moving_mask):
        # Project Accel onto Velocity
        vx_norm = vel_x[moving_mask] / speeds[moving_mask]
        vy_norm = vel_y[moving_mask] / speeds[moving_mask]

        ax = accel_x[moving_mask]
        ay = accel_y[moving_mask]

        long_accels[moving_mask] = ax * vx_norm + ay * vy_norm
        lat_accels[moving_mask]  = ax * (-vy_norm) + ay * vx_norm

    # --- 3. CALCULATE PEAKS ---
    max_brake = np.min(long_accels) if len(long_accels) > 0 else 0.0
    max_accel = np.max(long_accels) if len(long_accels) > 0 else 0.0
    max_lat_g = np.max(np.abs(lat_accels)) if len(lat_accels) > 0 else 0.0

    # --- 4. CALCULATE JERK & PENALTIES ---
    # Jerk is the derivative of acceleration (dt = 0.25s)
    lat_jerk = np.diff(lat_accels) / 0.25
    long_jerk = np.diff(long_accels) / 0.25

    # Peak Jerks
    max_long_jerk = np.max(np.abs(long_jerk)) if len(long_jerk) > 0 else 0.0
    max_lat_jerk  = np.max(np.abs(lat_jerk)) if len(lat_jerk) > 0 else 0.0

    # Unexpected Motion Penalty
    # Intent 1 = GO_STRAIGHT. If going straight but swerving hard, double the penalty.
    unexpected_motion_penalty = 1.0
    if ego_intent == 1 and max_lat_g > 1.5:
        unexpected_motion_penalty = 2.0

    # --- 5. CALCULATE DISPLACEMENT METRICS ---
    dx = np.diff(pos_x)
    dy = np.diff(pos_y)

    v_step_x = vel_x[:-1]
    v_step_y = vel_y[:-1]
    speed_step = np.sqrt(v_step_x**2 + v_step_y**2)
    step_mask = speed_step > 1.0

    lateral_moves_m = np.zeros_like(dx)

    if np.any(step_mask):
        vx_n = v_step_x[step_mask] / speed_step[step_mask]
        vy_n = v_step_y[step_mask] / speed_step[step_mask]
        lateral_moves_m[step_mask] = (dx[step_mask] * -vy_n) + (dy[step_mask] * vx_n)

    # --- 6. AGGREGATE METRICS & SCORE ---

    num_decelerations = np.sum(long_accels < -0.1)
    num_accelerations = np.sum(long_accels > 0.1)
    num_lat_events    = np.sum((np.abs(lat_accels) > 1.0) & (speeds > 2.0))

    total_lat_dist = np.sum(np.abs(lateral_moves_m))
    net_lat_dist   = np.abs(np.sum(lateral_moves_m))

    # Speed Weighting
    speed_factor = max(0.5, float(np.mean(speeds)) / 10.0)

    # Noise Filter: Only count braking if it's stronger than -1.0 m/s^2
    significant_braking = abs(max_brake) if max_brake < -1.0 else 0.0

    interaction_score = float(
        (significant_braking * 5.0) +
        (max_lat_g * 4.0 * speed_factor * unexpected_motion_penalty) +
        (max_long_jerk * 0.5) +
        (num_lat_events * 2.0)
    )

    return {
        'scene_id': data.frame.context.name,
        'timestamp': data.frame.timestamp_micros,
        'avg_speed_ms': float(np.mean(speeds)),
        'intent': int(ego_intent),

        'num_decelerations': int(num_decelerations),
        'num_accelerations': int(num_accelerations),
        'num_lateral_frames': int(num_lat_events),

        'max_braking': float(max_brake),
        'max_acceleration': float(max_accel),
        'max_lateral_accel': float(max_lat_g),
        'max_long_jerk': float(max_long_jerk),
        'max_lat_jerk': float(max_lat_jerk),

        'total_lateral_dist_m': float(total_lat_dist),
        'net_lateral_dist_m': float(net_lat_dist),

        'interaction_score': float(interaction_score)
    }

def classify_scenario(metrics):
    """
    A 4-Tier Classifier that combines Intent, Physics, and Speed Context.
    """
    # 1. Unpack Metrics
    speed_ms = metrics['avg_speed_ms']
    intent   = metrics['intent'] # 0=Unk, 1=Str, 2=Left, 3=Right

    max_brake = metrics['max_braking']       # Negative
    max_accel = metrics['max_acceleration']  # Positive
    max_lat   = metrics['max_lateral_accel'] # Absolute
    max_jerk  = metrics['max_long_jerk']

    brake_frames = metrics['num_decelerations']
    lat_frames   = metrics['num_lateral_frames']

    # === TIER 1: CRITICAL / EMERGENCY (Safety Flags) ===
    # These override everything else.

    if max_brake < -4.5:
        return "EMERGENCY BRAKING"

    # Intent says STRAIGHT (1), but physics says SWERVE (>2.0g)
    if intent == 1 and max_lat > 2.0:
        return "EVASIVE SWERVE / AVOIDANCE"

    # === TIER 2: AGGRESSIVE / ABNORMAL (Behavior Flags) ===

    # Intent says TURN (2/3), and physics says HARD (>2.5g)
    if intent in [2, 3] and max_lat > 2.5:
        return "Aggressive Cut-In / Turn"

    # High Jerk (> 4.0) means "Stomping" on gas/brakes
    if max_jerk > 4.0 and speed_ms > 5.0:
        return "Erratic / Jerky Driving"

    # Hard Launch from low speed
    if max_accel > 3.0 and speed_ms < 15.0:
        return "Aggressive Launch"

    # === TIER 3: COMPLEX TRAFFIC PATTERNS (Interaction Flags) ===

    # Stop-and-Go: Frequent braking (3+ frames) at City speeds (< 20mph)
    if brake_frames >= 3 and speed_ms < 9.0:
        return "Stop-and-Go Traffic"

    # Lane Weaving: Sustained lateral movement without Intent to Turn
    # (Drifting in lane)
    if lat_frames >= 2 and intent == 1:
        return "Lane Weaving / Unstable"

    # Normal Lane Change (Intent confirmed)
    if intent in [2, 3] and lat_frames >= 1:
        return "Normal Lane Change / Turn"

    # === TIER 4: STEADY STATE (Context Flags) ===
    # If nothing specific happened, describe the environment based on speed.

    if speed_ms < 1.0:
        return "Stationary / Idling"

    # < 15 mph (7 m/s)
    if speed_ms < 7.0:
        return "Parking Lot / Residential Area"

    # < 35 mph (16 m/s)
    if speed_ms < 16.0:
        return "City Surface Street"

    # < 55 mph (25 m/s)
    if speed_ms < 25.0:
        return "Fast Arterial Road"

    # > 55 mph
    return "Highway Cruising"

# Load one record
dataset = tf.data.TFRecordDataset(TFRECORD_FILE)
raw = next(iter(dataset))

# Count total frames in the dataset
total_frames = 0
try:
    for _ in tf.data.TFRecordDataset(TFRECORD_FILE): # Reload dataset to count from beginning
        total_frames += 1
    print(f"Total frames available in the dataset: {total_frames}")
except tf.errors.DataLossError as e:
    print(f"Warning: DataLossError encountered while counting frames. Dataset might be truncated or corrupted. Read {total_frames} frames before error.")
    print(f"Error details: {e}")
except Exception as e:
    print(f"An unexpected error occurred while counting frames: {e}")

# Parse E2E frame (this is the correct message!)
frame = wod_e2ed_pb2.E2EDFrame()
frame.ParseFromString(raw.numpy())

# Process dataset
print("🔄 Processing data...")
all_metrics = []
scenario_counts = defaultdict(int)

# 1. Dataset Iter
dataset_iter = dataset.as_numpy_iterator()
dataset_iter = iter(dataset_iter)

# 2. Process
for idx, bytes_example in enumerate(dataset_iter):
    if idx >= NUM_SAMPLES: break

    try:
        data = wod_e2ed_pb2.E2EDFrame()
        data.ParseFromString(bytes_example)

        # Analysis
        metrics = analyze_driving_behavior(data)

        if metrics:
            # Classification
            scenario = classify_scenario(metrics)
            metrics['scenario'] = scenario

            # Store
            scenario_counts[scenario] += 1
            all_metrics.append(metrics)

        if (idx + 1) % 50 == 0:
            print(f"  Processed {idx + 1} records...")

    except Exception as e:
        print(f"⚠️ Error record {idx}: {e}")
        continue

# 3. Results
print(f"\n✅ Analyzed {len(all_metrics)} samples")
print("-" * 55)
print(f"{'SCENARIO':<35} | {'COUNT':<5} | {'%':<5}")
print("-" * 55)
for scenario, count in sorted(scenario_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"{scenario:<35} | {count:<5} | {count/len(all_metrics)*100:.1f}%")

# Store the classified metrics in a csv file
df = pd.DataFrame(all_metrics)
df.to_csv("classified_metrics.csv", index=False)
print("\n📁 Saved CSV inside function.")
