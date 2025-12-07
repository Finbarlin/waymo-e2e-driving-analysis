### ECE143 Final Project Group 4
### Waymo E2E Driving Analysis - Surround View Visualization

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from PIL import Image
import io
import numpy as np
import pandas as pd
import tensorflow as tf
from waymo_open_dataset.protos import end_to_end_driving_data_pb2 as wod_e2ed_pb2

def rotate_to_vertical(xs, ys, headings):
    """
    Helper function: Rotates the trajectory so the initial heading points Up (+Y).
    This helps to intuitively visualize lateral deviation relative to the lane.
    
    :param xs: Array of X coordinates
    :param ys: Array of Y coordinates
    :param headings: Array of heading angles (radians)
    :return: Rotated X and Y arrays
    """
    # 1. Center the data (Start at 0,0)
    x_centered = xs - xs[0]
    y_centered = ys - ys[0]

    # 2. Calculate rotation angle (Map start_heading to Pi/2 or 90 degrees)
    start_heading = headings[0]
    theta = (np.pi / 2) - start_heading
    c, s = np.cos(theta), np.sin(theta)

    # 3. Apply rotation matrix
    x_rot = x_centered * c - y_centered * s
    y_rot = x_centered * s + y_centered * c

    return x_rot, y_rot

def visualize_hd_dashboard(dataset_input, all_metrics, top_n=5):
    """
    Generates an HD Dashboard: 
    - Left Panel: Trajectory analysis (Physics)
    - Right Panel: Multi-view Camera feed (Context)
    
    :param dataset_input: Path to TFRecord file (str) or loaded tf.data.Dataset object
    :param all_metrics: List of dicts parsed from csv (must contain 'interaction_score')
    :param top_n: Number of top scoring events to visualize
    """
    
    # --- 1. Data Preparation ---
    df = pd.DataFrame(all_metrics)
    
    # Sort by interaction score to find the most critical events
    top_events = df.sort_values('interaction_score', ascending=False).head(top_n)
    target_ids = set(top_events['scene_id'].values)
    
    # Create a map for quick lookup
    event_map = {row['scene_id']: row for _, row in top_events.iterrows()}

    print(f"📸 Generating HD Dashboard for Top {top_n} Events...")

    # Handle input type: Load dataset if it is a path string
    if isinstance(dataset_input, str):
        dataset = tf.data.TFRecordDataset(dataset_input, compression_type='')
    else:
        dataset = dataset_input

    dataset_iter = dataset.as_numpy_iterator()
    found_count = 0

    # --- 2. Iterate through dataset to find target scenes ---
    for bytes_example in dataset_iter:
        data = wod_e2ed_pb2.E2EDFrame()
        data.ParseFromString(bytes_example)
        curr_id = data.frame.context.name

        # Check if current frame is one of our targets
        if curr_id in target_ids:
            row = event_map[curr_id]
            found_count += 1
            print(f"Found Event {found_count}/{top_n}: {curr_id} (Score: {row['interaction_score']:.2f})")

            # --- 3. Setup Figure Layout ---
            # High resolution figure
            fig = plt.figure(figsize=(24, 12), dpi=100)

            # Layout: Left column for Trajectory, Right columns for Cameras
            num_cams = len(data.frame.images)
            cam_cols = 4 
            cam_rows = (num_cams + cam_cols - 1) // cam_cols

            # GridSpec: Trajectory column is 2.5x wider than a single camera column
            gs = gridspec.GridSpec(cam_rows, cam_cols + 1, width_ratios=[2.5] + [1]*cam_cols)
            gs.update(wspace=0.1, hspace=0.2)

            # =========================================================
            # PANEL 1: EGO TRAJECTORY (Left Side)
            # =========================================================
            ax_traj = fig.add_subplot(gs[:, 0])

            # Extract Physics Data
            pos_x = np.array(data.past_states.pos_x)
            pos_y = np.array(data.past_states.pos_y)
            vel_x = np.array(data.past_states.vel_x)
            vel_y = np.array(data.past_states.vel_y)

            # Calculate Heading and Rotate Coordinates
            headings = np.arctan2(vel_y, vel_x + 1e-6)
            lat_x, long_y = rotate_to_vertical(pos_x, pos_y, headings)

            # Plot: Reference Lines (Assuming 3.7m Lane Width)
            ax_traj.axvline(0, color='black', linestyle='-', alpha=0.1, linewidth=1)
            ax_traj.axvline(-1.85, color='gray', linestyle=':', alpha=0.4, label='Lane Width (+/- 1.85m)')
            ax_traj.axvline(1.85, color='gray', linestyle=':', alpha=0.4)

            # Plot: Actual Trajectory
            ax_traj.plot(lat_x, long_y, color='#007ACC', linewidth=5, alpha=0.8, label='Actual Path')

            # Plot: Start and End points
            ax_traj.scatter(lat_x[0], long_y[0], c='green', s=200, edgecolors='white', linewidth=2, zorder=5, label='Start')
            ax_traj.scatter(lat_x[-1], long_y[-1], c='red', s=200, edgecolors='white', linewidth=2, zorder=5, label='End')

            # Info Box (Scorecard)
            stats_text = (
                f"SCENARIO    : {row['scenario']}\n"
                f"RISK SCORE  : {row['interaction_score']:.2f}\n"
                f"-----------------------------\n"
                f"Speed       : {row['avg_speed_ms']:.1f} m/s\n"
                f"Max Brake   : {row['max_braking']:.2f} m/s²\n"
                f"Max Lat G   : {row['max_lateral_accel']:.2f} m/s²\n"
                f"Net Move    : {row['net_lateral_dist_m']:.2f} m"
            )
            ax_traj.text(0.05, 0.02, stats_text, transform=ax_traj.transAxes,
                         verticalalignment='bottom', fontsize=12, fontfamily='monospace', weight='bold',
                         bbox=dict(boxstyle='round,pad=0.5', facecolor='#f8f9fa', alpha=0.95, edgecolor='#cccccc'))

            # Styling
            ax_traj.set_title(f"EVENT #{found_count}: EGO-MOTION ANALYSIS", fontsize=16, fontweight='bold', pad=20)
            ax_traj.set_xlabel("Lateral Deviation (meters)", fontsize=12)
            ax_traj.set_ylabel("Longitudinal Distance (meters)", fontsize=12)
            ax_traj.axis('equal')
            ax_traj.set_xlim(-8, 8) # Fixed X-axis to clearly show swerving
            ax_traj.grid(True, linestyle='--', alpha=0.5)
            ax_traj.legend(loc='upper right', fontsize=10, frameon=True)

            # =========================================================
            # PANEL 2: SURROUND CAMERAS (Right Side)
            # =========================================================
            cam_labels = {
                1: 'FRONT', 2: 'FRONT_LEFT', 3: 'FRONT_RIGHT',
                4: 'SIDE_LEFT', 5: 'SIDE_RIGHT',
                6: 'BACK_LEFT', 7: 'BACK', 8: 'BACK_RIGHT'
            }

            sorted_images = sorted(data.frame.images, key=lambda x: x.name)

            for i, img_data in enumerate(sorted_images):
                row_idx = i // cam_cols
                col_idx = i % cam_cols

                # Add subplot
                ax_cam = fig.add_subplot(gs[row_idx, col_idx + 1])

                try:
                    img = Image.open(io.BytesIO(img_data.image))
                    ax_cam.imshow(img)

                    # Camera Label
                    label_text = cam_labels.get(img_data.name, f"CAM {img_data.name}")
                    ax_cam.text(0.5, 0.95, label_text, transform=ax_cam.transAxes,
                                ha='center', va='top', fontsize=11, fontweight='bold',
                                color='white', bbox=dict(facecolor='black', alpha=0.7, boxstyle='round,pad=0.2'))

                    # Remove ticks
                    ax_cam.set_xticks([])
                    ax_cam.set_yticks([])
                except:
                    ax_cam.text(0.5, 0.5, "IMAGE ERROR", ha='center')
                    ax_cam.axis('off')

            plt.show()

            # Remove from target list and check if done
            target_ids.remove(curr_id)
            if found_count >= top_n: break
            
    if found_count == 0:
        print("Warning: No matching scene IDs found in the provided TFRecord file. Please check if the file matches the CSV data.")
